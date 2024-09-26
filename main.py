import sys
import numpy as np
import time
import matplotlib.pyplot as plt

sys.path.append('C:\\Users\\whw29\\Desktop\\RCM\\RCM')

from RCM import FullControlMicroscope
'''
Note due to setting the Oceandirect SDK as content root so that it can be imported, 
whenever specifying file path, use the file path from root
'''

if __name__ == '__main__':

    msc = FullControlMicroscope(no_spectra=20, exposure_time=100e-3, save_folder="C:\\Users\\whw29\\Desktop\\Images4", check_stage=False)

    msc.led.set_current_mA(1000)
    msc.led.on()

    msc.lcf.set_bandwidth(bandwidth=2)

    msc.take_HS_time_series_images(time_increment=600, total_time=72000)
    msc.led.off()
    msc.close()
