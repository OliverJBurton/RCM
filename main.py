import sys

sys.path.append('../RCM/RCM')

from RCM import FullControlMicroscope
from OpticalPowerMeter import PM16_120

if __name__ == '__main__':
    # cam = Camera_HS()
    # img = cam.single_exposure(exposure_time=0.654e-3)
    # plt.imshow(img)
    # plt.show()

    msc = FullControlMicroscope(exposure_time=0.645e-3, save_folder="C:\\Users\\whw29\\Desktop\\Images")

    power_meter = PM16_120()

    currents = np.linspace(0, 500, 15)
    powers_mu = []

    for current in currents:
        msc.led.set_current(current)
        # Wait for reading to stabilise
        time.sleep(3)

        powers_mu.append(round(power_meter.get_power_reading_W*10**6), 1)
    
    with open("power_PM16.txt", "w+") as file:
        for power in powers_mu:
            file.write(f"{power},")
        file.write("\n")
    
    plt.plot(current, powers_mu)
    plt.xlabel("Current (mA)")
    plt.ylabel("Power ($\mu$W)")
    plt.xlim((450, 700))
    plt.show()
        

    # msc.mapping(sample_dim=[50, 50], sample_no_per_channel=[1, 1], RGB_img_too=True)

    # # msc.aquire_TL_time_series(time_increment=1,total_time=2,folder=folder,exposure_time=0.654e-3)
    # msc.aquire_HS_datacube(exposuretime=0.654e-3, save_folder="C:\\Users\\whw29\\Desktop\\Images")
    msc.close()
