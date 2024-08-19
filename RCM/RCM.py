import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool

from camera import Camera_HS #Spectral
from camera import Camera_BA #RGB
from light import DC2200
from stage import Controller
from tunablefilter import TunableFilter
from OpticalPowerMeter import PM100
import time
import os
import cv2
import imageio


class FullControlMicroscope:
    def __init__(self, wavelength_range=[420, 730], no_spectra=5, exposure_time=0.0, save_folder=""):
        self.wavelength_range = wavelength_range
        self.no_spectra = no_spectra
        self.exposure_time = exposure_time
        self.save_folder = save_folder
        self.intensity_loss_pixel_matrix = []
        self.greyscale_intensity_list = []

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
        self.power_meter = PM100()
        print("Power meter connected")

        self.sta = Controller(which_port='COM4',
                              stages=('ZFM2030', 'ZFM2030', 'ZFM2030'),
                              reverse=(False, False, True),
                              verbose=True,
                              very_verbose=False)
        print('stage connected')

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

    def obtain_intensity_pixel_matrix(self, xNum=20, yNum=20):
        '''
        Determines how each block of pixel on the screen affects the light intensity incident on the sample. Note the canvas width and height should be multiples of xNum and yNum respectively.
        Sets the parameter intensity_loss_pixel_matrix

        :param xNum: splits the width of the canvas into xNum blocks
        :param yNum: splits the height of the canvas into yNum blocks
        '''

        # Add something to open and move inkscape to the 3rd screen or tell user to do it
        # https://github.com/spakin/SimpInkScr/wiki/Modifying-existing-objects

        x_coords = np.linspace(0, canvas.width, xNum)
        y_coords = np.linspace(0, canvas.height, yNum)
        intensity_readings = [[0 for i in range(yNum)] for j in range[xNum]]

        full_brightness_reading = self.power_meter.read()

        for x_coord in x_coords:
            for y_coord in y_coords:
                rect((x_coord, y_coord), (x_coord+x_coords[0], y_coord+y_coords[0]), fill="#000000")
                intensity_readings[x_coord][y_coord] = full_brightness_reading - self.power_meter.read()
        
        self.intensity_loss_pixel_matrix = intensity_readings

    def greyscale_intensity_relationship(self, step=5):
        '''
        Determines the relationship between the greyscale of the image and light intensity
        Sets the parameter greyscale_intensity_list and plots a graph of light intensity vs greyscale
        :param steps: size of the interval between greyscale values
        '''

        # Return a fitted curve, need to check which equation to use first
        # Could use np.poly1d(np.polyfit(x, y))
        
        rect((0, 0), (canvas.width, canvas.height), fill="#ffffff")
        greyscale_intensity_readings = []

        for i in range(0, 255, step):
            greyscale = "# + {:02x}".format(i)*3
            greyscale_intensity_readings.append([greyscale, self.power_meter.read()])
        
        n_readings = np.array(greyscale_intensity_readings)
        plt.plot(n_readings[:,0], n_readings[:,1])
        plt.xlabel("Greyscale")
        plt.ylabel("Light intensity (W/m^2)")
        plt.show()
        self.greyscale_intensity_list = greyscale_intensity_readings

    def save_image(self, wavelengths, hypercube, indices):
        '''
        Saves image in save_folder
        :param wavelengths: list of wavelengths in nm
        :param hypercube: list of 3D images
        :param indices: list of identifiers to append to the name of each image
        '''
        for ii, wl in enumerate(wavelengths):
            image_name = 'image_cap_' + str(ii) + '_' + str(wl) + '_' + '_'.join(str(e) for e in indices) + '_img.png'
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
        wavelengths = np.linspace(self.wavelength_range[0], self.wavelength_range[1], self.no_spectra)
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
        t0 = time.time()
        while time.time() - t0 < total_time:
            time.sleep(time_increment)
            wavelengths, hypercube = self.aquire_HS_datacube()
            self.save_image(wavelengths, hypercube, [time.time() - t0])            

    def mapping(self, sample_dim=[], sample_no_per_channel=[], RGB_img_too=False):
        '''
        Performs mapping based off size of each sample or the number of samples or both and saves image. Keep sample_no_per_channel as an empty list if you want to perform mapping based off sample size and vice versa. 
        :param: sample_dim: [dimensions of sample along channel 0, dimensions of sample along channel 1]
        :param: sample_no_per_channel: [number of samples along channel 0, number of samples along channel 1]
        :param: RGB_img_too: takes RGB image as well as hyperspectral image if True
        '''

        # Either create list of locations based off size of each sample or the number of samples or both
        positions_list = []
        if sample_dim != [] and sample_no_per_channel != []:
            for c in self.sta.channels[:2]:
                # Starting from lower limit, generate required number of boxes unless coordinate of the box gets too close to upper limit
                positions_list.append([-self.sta._position_limit_um[c]+sample_dim[c]*(i+1/2) for i in range(sample_no_per_channel[c]) if -self.sta._position_limit_um[c]+sample_dim[c]*(i+1/2) <= self.sta._position_limit_um[c]-sample_dim[c]])
        elif sample_dim != []:
            for c in self.sta.channels[:2]:
                # Positions of stage, camera must be centered on the box
                positions_list.append(np.arange(-self.sta._position_limit_um[c]+sample_dim[c]/2, self.sta._position_limit_um[c]-sample_dim[c]/2, sample_dim[c]))
        elif sample_no_per_channel != []:
            for c in self.sta.channels[:2]:
                # Determine shift required to get from side of each box to the center of each box
                shift = self.sta._position_limit_um[c]/sample_no_per_channel[c]

                # Determine position of the corner of each box, add shift to move position to center of box
                positions_list.append(np.linspace(-self.sta._position_limit_um[c], self.sta._position_limit_um[c], sample_no_per_channel[c], endpoint=False) + shift)
        else:
            print("Enter valid parameters")
            return None

        # iterate throughout all possible boxes
        for i in positions_list[0]:
            self.sta.move_um(self.sta.channels[0], i, relative=False)
            for j in positions_list[1]:
                self.sta.move_um(self.sta.channels[1], j, relative=False)

                if RGB_img_too:
                    pool = Pool()
                    spectral = pool.apply_async(self.aquire_HS_datacube, [wavelength_range, no_spectra, exposure_time])
                    rgb = pool.apply_async(self.cba.average_exposure, [exposure_time])

                    wavelengths, hypercube = spectral.get()
                    rgbImage = rgb.get()
                    self.save_image(wavelengths, hypercube, save_folder, [i, j])
                    imageio.imwrite(fn, rgbImage)

                # Take hyperspectral imaging of each box
                wavelengths, hypercube = self.aquire_HS_datacube()
                self.save_image(wavelengths, hypercube, [i, j])