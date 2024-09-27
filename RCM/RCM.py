import numpy as np

from camera import Camera_HS #Spectral
from camera import Camera_BA #RGB
from light import DC2200
from stage import Controller
from tunablefilter import TunableFilter
import time
import os
import imageio
import sys

sys.path.append("C:\\Users\\whw29\\Desktop\\RCM\\Image Processing")
from AveragePowerOverTimeAndWavelength import AveragePowerOverTimeAndWavelength

class FullControlMicroscope:
    def __init__(self, wavelength_range=[420, 730], no_spectra=5, exposure_time=0.0, save_folder="", check_stage=True):
        self.wavelength_range = wavelength_range
        self.no_spectra = no_spectra
        self.exposure_time = exposure_time
        self.save_folder = save_folder

        # initialising all sections:
        self.chs = Camera_HS()
        print('HS camera connected')
        self.cba = Camera_BA()
        print('TL camera connected')
        self.led = DC2200()
        print('LS connected')
        self.lcf = TunableFilter()
        print('LC connecting...')
        self.lcf.open()
        print('LC connected')
        self.image_processing = AveragePowerOverTimeAndWavelength(image_folder=save_folder, thread_sleep_time=120, save_file="C:\\Users\\whw29\\Desktop\\RCM\\Image Processing\\average_power_Au3.txt")

        self.sta = Controller(which_port='COM4',
                              stages=('ZFM2030', 'ZFM2030', 'ZFM2030'),
                              reverse=(False, False, True),
                              verbose=True,
                              very_verbose=False)
        print('stage connected')

        if check_stage:
            self.stage_check()

    def stage_check(self):
        print("Please ensure the position values of each motor are within their respective limits. If not, move the stage back to it's unextended position to recalibrate its zero position. Also do this if the zero position of the stage has been altered on the MCM3000 Microscopy Controllers Software.")
        while True:
            response = input("Does the zero position of the stage requiring recalibrating? Y/N")
            if response == "N":
                break
            elif response == "Y":
                for channel in self.sta.channels:
                    self.sta.set_encoder_counts_to_zero(channel)
                print("Completed recalibration")
                break

    def close(self):
        '''
        Closes all peripherals
        :return:
        '''
        self.chs.close()
        self.cba.close()
        self.led.close()
        self.sta.close()
        self.lcf.close()

    def save_image(self, wavelengths, hypercube, indices):
        '''
        Saves image in save_folder
        :param wavelengths: list of wavelengths in nm
        :param hypercube: list of 3D images
        :param indices: list of identifiers to append to the name of each image
        '''
        for ii, wl in enumerate(wavelengths):
            image_name = 'image_cap_' + str(ii) + '_' + str(wl) + '_' + '_'.join(str(round(e)) for e in indices) + '_img.png'
            fn = os.path.join(self.save_folder, image_name)
            imageio.imwrite(fn, hypercube[ii].astype(np.uint16))

    def aquire_HS_datacube(self):
        '''
        Takes images filtered at a range of wavelengths
        :param wavelength_range: range in nm of wavelengths
        :param no_spectra: number of spectral points
        :param exposuretime: exposure time of camera
        :param save_folder: empty list or name of folder
        :return: (list of wavelengths in nm, list of 3D images)
        '''

        # Create list of wavelengths
        wavelengths = np.round(np.linspace(self.wavelength_range[0], self.wavelength_range[1], self.no_spectra))
        hypercube = []

        for wl in wavelengths:
            self.lcf.set_wavelength(int(wl))
            time.sleep(3e-2)
            hypercube.append(self.chs.single_exposure(exposure_time=self.exposure_time))

        return wavelengths, hypercube

    def take_HS_time_series_images(self, time_increment=10, total_time=7200):
        '''
        Does a hyperspectral imaging over time and saves the images
        :param time_increment: time between measurements
        :param total_time: time for all data measurements
        '''
        self.image_processing.average_count_thread.start()
        t0 = time.time()
        while time.time() - t0 < total_time:
            time.sleep(time_increment)
            wavelengths, hypercube = self.aquire_HS_datacube()
            self.image_processing.taking_images.set()
            self.save_image(wavelengths, hypercube, [time.time() - t0])
            self.image_processing.taking_images.clear()
        self.image_processing.is_finished.set()
        self.image_processing.average_count_thread.join()

    def mapping(self, channels=[1, 2], sample_dim=[], sample_no_per_channel=[]):
        '''
        Performs mapping based off size of each sample or the number of samples or both and saves image. Keep sample_no_per_channel as an empty list if you want to perform mapping based off sample size and vice versa.
        :param: specifies which channel corresponds to the x-axis and y-axis motor, e.g. [0, 2] means channel 0 is x-axis and channel 2 is y-axis
        :param: sample_dim: [dimensions of sample along channel 0, dimensions of sample along channel 1]
        :param: sample_no_per_channel: [number of samples along channel 0, number of samples along channel 1]
        '''

        # Either create list of locations based off size of each sample or the number of samples or both
        positions_list = []
        if sample_dim != [] and sample_no_per_channel != []:
            for c in range(2):
                # Starting from lower limit, generate required number of boxes unless coordinate of the box gets too close to upper limit
                positions_list.append([-self.sta._position_limit_um[channels[c]]+sample_dim[c]*(i+1/2) for i in range(sample_no_per_channel[c]) if -self.sta._position_limit_um[channels[c]]+sample_dim[c]*(i+1/2) <= self.sta._position_limit_um[channels[c]]-sample_dim[c]])
        elif sample_dim != []:
            for c in range(2):
                # Positions of stage, camera must be centered on the box
                positions_list.append(np.arange(-self.sta._position_limit_um[channels[c]]+sample_dim[c]/2, self.sta._position_limit_um[channels[c]]-sample_dim[c]/2, sample_dim[c]))
        elif sample_no_per_channel != []:
            for c in range(2):
                # Determine shift required to get from side of each box to the center of each box
                shift = self.sta._position_limit_um[channels[c]]/sample_no_per_channel[c]

                # Determine position of the corner of each box, add shift to move position to center of box
                positions_list.append(np.linspace(-self.sta._position_limit_um[channels[c]], self.sta._position_limit_um[channels[c]], sample_no_per_channel[c], endpoint=False) + shift)
        else:
            print("Enter valid parameters")
            return None

        # iterate throughout all possible boxes
        for i in positions_list[0]:
            self.sta.move_um(channels[0], i, relative=False)
            for j in positions_list[1]:
                self.sta.move_um(channels[1], j, relative=False)

                # Take hyperspectral imaging of each box
                wavelengths, hypercube = self.aquire_HS_datacube()
                self.save_image(wavelengths, hypercube, [i, j])


if __name__ == "__main__":
    msc = FullControlMicroscope(exposure_time=0.645e-3, save_folder="C:\\Users\\whw29\\Desktop\\Images")
    msc.obtain_intensity_pixel_matrix()
    msc.close()

    # msc.obtain_intensity_pixel_matrix()
    # msc.close()