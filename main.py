import sys

sys.path.append('../RCM/RCM')

from RCM import FullControlMicroscope

if __name__ == '__main__':
    # cam = Camera_HS()
    # img = cam.single_exposure(exposure_time=0.654e-3)
    # plt.imshow(img)
    # plt.show()

    msc = FullControlMicroscope(exposure_time=0.645e-3, save_folder="C:\\Users\\whw29\\Desktop\\Images")

    msc.obtain_intensity_pixel_matrix()

    # msc.mapping(sample_dim=[50, 50], sample_no_per_channel=[1, 1], RGB_img_too=True)

    # # msc.aquire_TL_time_series(time_increment=1,total_time=2,folder=folder,exposure_time=0.654e-3)
    # msc.aquire_HS_datacube(exposuretime=0.654e-3, save_folder="C:\\Users\\whw29\\Desktop\\Images")
    msc.close()
