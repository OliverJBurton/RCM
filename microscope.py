import sys
sys.path.append( '../RCM/RCM')
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
        #self.cba = Camera_BA()
        #print('TL camera connected')
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
        #self.cba.close()
        self.led.close()
        self.sta.close()
        self.lcf.close()

    def aquire_HS_datacube(self,wavelength_range=[420,730],step_size=5):
        wavelengths = np.arange(wavelength_range[0], wavelength_range[1], step_size)

        folder = r'C:\Users\ob303\OneDrive - University of Cambridge\Projects_current\Experimental\2024_Oana_Bluephase\Bluephase_BP5_001'

        # Capturing images with multiple exposures and storing the mean image in 'capture'
        for wl in np.linspace(420, 500, 80):
            self.lcf.set_wavelength(int(wl))
            time.sleep(3e-2)
            img = self.chs.single_exposure(exposure_time=120e-3)
            fn = os.path.join(folder, 'image_cap_%04d' % (i) + '_' + str(wl) + 'img.png')
            imageio.imwrite(fn, img.astype(np.uint16))

    def aquire_HS_reference(self,wavelength_range=[420,730],step_size=5):
        pass

    def aquire_TL_time_series(self,time_increment=10,total_time=7200,folder='',exposure_time=0.654e-3):
        '''
        :param time_increment:
        :param total_time:
        :return:
        '''
        t0 = time.time()
        ti = time.time()
        n = 0
        while ti-t0 < total_time:
            ti = time.time()
            img = self.cba.single_exposure(exposure_time=exposure_time)
            fn = os.path.join(folder, 'image_cap_%04d' % (n)+ '_' + str(ti-t0) + '_' + 'img.png')
            imageio.imwrite(fn, img)
            n+=1
            time.sleep(time_increment)



if __name__ == '__main__':
    if 0:
        cam = Camera_HS()
        img = cam.single_exposure(exposure_time=0.654e-3)
        plt.imshow(img)
        plt.show()

    msc = FullControlMicroscope()
    #msc.aquire_TL_time_series(time_increment=1,total_time=2,folder=folder,exposure_time=0.654e-3)
    msc.aquire_HS_datacube()
    msc.close()
