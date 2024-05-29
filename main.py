import sys

sys.path.append('../RCM/RCM')
import numpy as np
import matplotlib.pyplot as plt

from camera import Camera_HS
from camera import Camera_BA
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
        # self.cba = Camera_BA()
        # print('TL camera connected')
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
        # self.cba.close()
        self.led.close()
        self.sta.close()
        self.lcf.close()

    def aquire_HS_datacube(self, wavelength_range=[420, 730], no_spectra=5, exposuretime=[],save_folder=[]):
        '''

        :param wavelength_range: range in nm of wavelengths
        :param no_spectra: number of spectral points
        :param exposuretime: exposure time of camera
        :param save:
        :return:
        '''
        wavelengths = np.arange(wavelength_range[0], wavelength_range[1], step_size)


        if exposuretime == []:
            exposure_time = self.chs.exposure
        else:
            exposure_time = exposuretime
        # Capturing images with multiple exposures and storing the mean image in 'capture'
        wavelengths = []
        hypercube = []

        for wl in np.linspace(wavelength_range[0], wavelength_range[1], no_spectra):
            wavelengths.append(wl)
            self.lcf.set_wavelength(int(wl))
            time.sleep(3e-2)
            hypercube.append(self.chs.single_exposure(exposure_time=exposure_time))

        if save_folder == []:
            return wavelengths, hypercube
        else:
            for ii, wl in enumerate(wavelengths):
                fn = os.path.join(save_folder, 'image_cap_%04d' % (i) + '_' + str(wl) + '_img.png')
                imageio.imwrite(fn, hypercube[ii].astype(np.uint16))

    def aquire_HS_time_series(self, wavelength_range=[420, 730], no_spectra=5, exposuretime=[],
                              save_folder=[], time_increment=10, total_time=7200):
        '''
        :param time_increment:
        :param total_time:
        :return:
        '''
        t0 = time.time()
        ti = time.time()
        tx = time.time()
        n = 0
        while ti - t0 < total_time:
            time.sleep(1e-3)
            ti = time.time()
            if tx-ti > time_increment:
                wavelengths, hypercube = self.aquire_HS_datacube(wavelength_range=wavelength_range, no_spectra=no_spectra, exposuretime=exposuretime,
                              save_folder=[])
                for ii, wl in enumerate(wavelengths):
                    fn = os.path.join(save_folder, 'image_cap_%04d' % (n) + '_' + str(wl) + '_' + str(ti - t0) + '_' + 'img.png')
                    imageio.imwrite(fn, hypercube[ii].astype(np.uint16))
                n += 1


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
