import sys
import numpy as np
import time
import matplotlib.pyplot as plt

sys.path.append('../RCM/RCM')

from RCM import FullControlMicroscope
from OpticalPowerMeter import PM16_120

if __name__ == '__main__':
    # cam = Camera_HS()
    # img = cam.single_exposure(exposure_time=0.654e-3)
    # plt.imshow(img)
    # plt.show()
    #
    # msc = FullControlMicroscope(exposure_time=0.645e-3, save_folder="C:\\Users\\whw29\\Desktop\\Images", check_stage=False)
    #
    # # power_meter = PM16_120()
    # #
    currents = np.linspace(0, 500, 20)
    # # powers_mu = []
    #
    # msc.led.on()
    #
    # for current in currents:
    #     msc.led.set_current_mA(current)
    #     # Wait for reading to stabilise
    #     time.sleep(5)
    #
    #     # powers_mu.append(round(power_meter.get_power_reading_W()*10**6, 1))
    #
    # msc.led.off()
    
    with open("power_PM16_405nm.txt", "r") as file:
        pm16_readings = np.array(list(file.readline().split(","))[:-1], np.float32)

    with open("power_PM100_365nm.txt", "r") as file:
        pm100_readings = np.array(list(file.readline().split(","))[:-1], np.float32)

    z = np.polyfit(currents, pm16_readings, 1)
    print(z)
    f1 = np.poly1d(z)

    z = np.polyfit(currents, pm100_readings, 1)
    print(z)
    f2 = np.poly1d(z)

    plt.plot(currents, pm16_readings)
    plt.plot(currents, pm100_readings/0.386*0.397)

    # plt.plot(currents, f1(currents))
    # plt.plot(currents, f2(currents))
    plt.xlabel("Current (mA)")
    plt.ylabel("Power (microW)")
    plt.xlim((0, 500))
    plt.ylim((0, 200))
    plt.show()


    # msc.mapping(sample_dim=[50, 50], sample_no_per_channel=[1, 1], RGB_img_too=True)

    # # msc.aquire_TL_time_series(time_increment=1,total_time=2,folder=folder,exposure_time=0.654e-3)
    # msc.aquire_HS_datacube(exposuretime=0.654e-3, save_folder="C:\\Users\\whw29\\Desktop\\Images")
    # msc.close()
