import sys

sys.path.append('../RCM/RCM')
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool

from camera import Camera_HS #Spectral
from camera import Camera_BA #RGB
from light import DC2200
from stage import Controller
from tunablefilter import TunableFilter
import time
import os
import cv2
import imageio


class FullControlMicroscope:
    def __init__(self):
        # initialising all sections:
        self.chs = Camera_HS()
        print('HS camera connected')
        self.cba = Camera_BA()
        print('TL camera connected')
        self.led = DC2200()
        print('LS connected')
        self.sta = Controller(which_port='COM4',
                              stages=('ZFM2030', 'ZFM2030', 'ZFM2030'),
                              reverse=(False, False, True),
                              verbose=True,
                              very_verbose=False)
        print('stage connected')

        self.lcf = TunableFilter()
        print('LC connecting...')

        self.lcf.open()
        print('LC connected')

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

    def save_image(self, wavelengths, hypercube, save_folder, data):
        for ii, wl in enumerate(wavelengths):
            image_name = 'image_cap_' + str(ii) + '_' + str(wl) + '_' + '_'.join(str(e) for e in data) + '_img.png'
            fn = os.path.join(save_folder, image_name)
            imageio.imwrite(fn, hypercube[ii].astype(np.uint16))     

    def aquire_HS_datacube(self, wavelength_range=[420, 730], no_spectra=5, exposuretime=0,save_folder=""):
        '''

        :param wavelength_range: range in nm of wavelengths
        :param no_spectra: number of spectral points
        :param exposuretime: exposure time of camera
        :param save_folder: empty list or name of folder
        :return wavelengths: 1D list of wavelengths
        :return hypercube: list of 3D images
        '''

        if exposuretime == 0:
            exposuretime = self.chs.exposure
        else:
            exposuretime = exposuretime

        # Capturing images with multiple exposures and storing the mean image in 'capture'
        wavelengths = np.linspace(wavelength_range[0], wavelength_range[1], no_spectra)
        hypercube = []

        for wl in wavelengths:
            self.lcf.set_wavelength(int(wl))
            time.sleep(3e-2)
            hypercube.append(self.chs.single_exposure(exposure_time=exposure_time))

        if save_folder == "":
            return wavelengths, hypercube
        else:
            self.save_image(wavelengths, hypercube, save_folder, [])

    def aquire_HS_time_series(self, wavelength_range=[420, 730], no_spectra=5, exposuretime=0,
                              save_folder="", time_increment=10, total_time=7200):
        '''
        :param time_increment:
        :param total_time:
        :return:
        '''
        t0 = time.time()
        while time.time() - t0 < total_time:
            time.sleep(time_increment)
            wavelengths, hypercube = self.aquire_HS_datacube(wavelength_range=wavelength_range, no_spectra=no_spectra, exposuretime=exposuretime,
                            save_folder=[])
            self.save_image(wavelengths, hypercube, save_folder, [time.time() - t0])            

    def mapping(self, channels=[0,1], sample_dim=[], sample_no_per_channel=[], wavelength_range=[420, 730], no_spectra=5, save_folder="", RGB_img_too=False, exposure_time=0):
        """
        Steps
        0. Check if channel is available
        1. Move stage to initial position
        Loop
        2. Get reading
        3. Move to next position
        EndLoop
        4. Save reading
        """

        # Validation checks
        assert channel in self.sta.channels, ("%s is not in list of channels" % (channel))
        assert (sample_dim[0] != 0 and sample_dim[1] != 0), ("Dimensions of sample cannot be 0")
        assert (sample_no_per_channel[0] > 0 and sample_dim[1] > 0), ("Number of samples along each channel cannot be 0 or negative")
        assert (type(sample_no_per_channel[0]) == type(1) and type(sample_no_per_channel[1]) == type(1)), ("Number of samples along each channel must be an integer")

        # Either create list of locations based off size of each sample or the number of samples or both
        positions_list = [[],[]]
        if sample_dim != [] and sample_no_per_channel != []:
            for c in channels[:2]:
                # Starting from lower limit, generate required number of boxes unless coordinate of the box gets too close to upper limit
                positions_list[c] = [-self.sta._position_limit_um[c]+sample_dim[c]*(i+1/2) for i in range(sample_no_per_channel[c]) if -self.sta._position_limit_um[c]+sample_dim[c]*(i+1/2) <= self.sta._position_limit_um[c]-sample_dim[c]]
        elif sample_dim != []:
            for c in channels[:2]:
                # Positions of stage, camera must be centered on the box
                positions_list[c] = np.arange(-self.sta._position_limit_um[c]+sample_dim[c]/2, self.sta._position_limit_um[c]-sample_dim[c]/2, sample_dim[c])
        elif sample_no_per_channel != []:
            for c in channels[:2]:
                # Determine dimensions of each sample
                shift = 2*self.sta._position_limit_um[c]/sample_no_per_channel[c]

                # Determine position of the corner of each box, add shift to move position to center of box
                positions_list[c] = np.linspace(-self.sta._position_limit_um[c], self.sta._position_limit_um[c], sample_no_per_channel[c], endpoint=False) + shift1
        else:
            print("Enter valid parameters")
            return None

        # iterate throughout all possible boxes
        for i in position1_list:
            self.sta.move_um(channels[0], i, relative=False)
            for j in position2_list:
                self.sta.move_um(channels[1], j, relative=False)

                # Use camera to take a snapshot of each box

                if RGB_img_too:
                    pool = Pool()
                    spectral = pool.apply_async(self.aquire_HS_datacube, [wavelength_range, no_spectra])
                    rgb = pool.apply_async(self.cba.average_exposure, [exposure_time])

                    wavelengths, hypercube = spectral.get()
                    rgbImage = rgb.get()
                    self.save_image(wavelengths, hypercube, save_folder, [i, j])
                    imageio.imwrite(fn, rgbImage)

                wavelengths, hypercube = self.aquire_HS_datacube(wavelength_range, no_spectra)
                self.save_image(wavelengths, hypercube, save_folder, [i, j])




if __name__ == '__main__':
    if 0:
        cam = Camera_HS()
        img = cam.single_exposure(exposure_time=0.654e-3)
        plt.imshow(img)
        plt.show()

    msc = FullControlMicroscope()
    # msc.aquire_TL_time_series(time_increment=1,total_time=2,folder=folder,exposure_time=0.654e-3)
    msc.aquire_HS_datacube()
    msc.close()
