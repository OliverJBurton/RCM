# First, we import the matplotlib library, which is useful for creating static, animated, and interactive visualizations in Python.
import matplotlib.pyplot as plt
import os
import time
# Importing the Thorlabs device library from the pylablib, which is a Python library for control and data acquisition in scientific experiments.
from pylablib.devices import Thorlabs as tl
import pylablib as pll

pll.par["devices/dlls/uc480"] = r"C:/Program Files/Thorlabs/Scientific Imaging/ThorCam"

# NumPy is a Python library used for working with arrays. It also has functions for working in domain of linear algebra, Fourier transform, and matrices.
import numpy as np

class Camera_HS():
    # Initializing method with self parameter, which refers to the instance of the class.
    def __init__(self):
        # Printing the camera's serial number using the list_cameras_tlcam function from the Thorlabs library
        print('Camera Serial : ',tl.list_cameras_tlcam())

        # Open the first camera found
        self.cam = tl.ThorlabsTLCamera(serial='24070')

        # Opening the camera
        self.cam.open()

        # This sets viewing limits (strange for camera but works for now)
        self.cam.set_roi(0, 4096, 0, 2616)

        # Verifying if the camera opened successfully and printing the status
        print('Camera opened : ', self.cam.is_opened())

        # Initializing some parameters. The max_val and min_val are generally used to represent the pixel range in the image.
        self.max_val = 4096
        self.min_val = 0

        # Set an initial exposure time in milliseconds
        self.exposure = 15 #ms

        # Setting the camera's exposure to the initial exposure time
        self.cam.set_exposure(self.exposure)

    def single_exposure(self,exposure_time = 1):
        self.cam.set_exposure(exposure_time)
        return self.cam.snap().astype(np.uint16)

    def average_exposure(self,exposure_time=1,averages=5):
        self.cam.set_exposure(exposure_time)
        exps = []
        for i in range(averages):
            exps.append(self.cam.snap().astype(np.uint16))
        return np.mean(exps,axis=0)

    # Method for acquiring images with multiple exposure times, ranging from 'start_exposure' (in seconds) with 'doubles' doublings.
    def multi_exposure(self,start_exposure=1e-4, doubles=10, discard_ratio=0.2):
        # Initializing list for storing raw data
        raw_data =[]
        # Iterating over defined number of 'doubles'
        for i in range(doubles):
            # Setting camera exposure
            self.cam.set_exposure(start_exposure*2**i)


            # Capturing image and converting it to numpy array of float32 type
            temp = self.cam.snap().astype(np.float32)

            # Setting any pixels that are greater than max_val*(1-discard_ratio) to NaN
            temp[temp>=self.max_val*(1-discard_ratio)] = np.NAN

            # Setting any pixels that are less than max_val*discard_ratio to NaN
            temp[temp<=self.max_val*(discard_ratio)] = np.NAN

            # Adding the image to raw_data list and normalizing it by the exposure ratio
            raw_data.append(temp/(2**i))

        # Converting raw_data to a numpy array
        raw_data = np.array(raw_data)

        # Calculating the mean of the images, ignoring NaNs
        mean_data = np.nanmean(raw_data,axis=0)

        # Returning the mean data
        return mean_data

    # Method to close the camera after use
    def close(self):
        self.cam.close()

class Camera_BA():
    # Initializing method with self parameter, which refers to the instance of the class.
    def __init__(self):
        # Printing the camera's serial number using the list_cameras_tlcam function from the Thorlabs library
        print('Camera Serial : ',tl.list_cameras_tlcam())

        # Open the first camera found
        self.cam = tl.ThorlabsTLCamera(serial='23588')

        # Opening the camera
        self.cam.open()

        # This sets viewing limits (strange for camera but works for now)
        self.cam.set_roi(0, 4096, 0, 2616)

        # Verifying if the camera opened successfully and printing the status
        print('Camera opened : ', self.cam.is_opened())

        # Initializing some parameters. The max_val and min_val are generally used to represent the pixel range in the image.
        self.max_val = 4096
        self.min_val = 0

        # Set an initial exposure time in milliseconds
        self.exposure = 50 #ms

        # Setting the camera's exposure to the initial exposure time
        self.cam.set_exposure(self.exposure)

    def single_exposure(self,exposure_time = 1):
        self.cam.set_exposure(exposure_time)
        plt.imshow(self.cam.grab(1))
        plt.show()
        return self.cam.snap()

    def average_exposure(self,exposure_time=1,averages=5):
        self.cam.set_exposure(exposure_time)
        exps = []
        for i in range(averages):
            exps.append(self.cam.snap())
        return np.mean(exps,axis=0)

    # Method for acquiring images with multiple exposure times, ranging from 'start_exposure' (in seconds) with 'doubles' doublings.
    def multi_exposure(self,start_exposure=1e-4, doubles=10, discard_ratio=0.2):
        # Initializing list for storing raw data
        raw_data =[]
        # Iterating over defined number of 'doubles'
        for i in range(doubles):
            # Setting camera exposure
            self.cam.set_exposure(start_exposure*2**i)


            # Capturing image and converting it to numpy array of float32 type
            temp = self.cam.snap().astype(np.float32)

            # Setting any pixels that are greater than max_val*(1-discard_ratio) to NaN
            temp[temp>=self.max_val*(1-discard_ratio)] = np.NAN

            # Setting any pixels that are less than max_val*discard_ratio to NaN
            temp[temp<=self.max_val*(discard_ratio)] = np.NAN

            # Adding the image to raw_data list and normalizing it by the exposure ratio
            raw_data.append(temp/(2**i))

        # Converting raw_data to a numpy array
        raw_data = np.array(raw_data)

        # Calculating the mean of the images, ignoring NaNs
        mean_data = np.nanmean(raw_data,axis=0)

        # Returning the mean data
        return mean_data

    # Method to close the camera after use
    def close(self):
        self.cam.close()


def live_time_lapse():
    folder = r'C:\Users\ob303\OneDrive - University of Cambridge\Projects_current\Experimental\2023_OxideNanowires\LinkhamStageTest_640nmW'

    cam = Camera_HS()
    t0 = time.time()

    # Capturing images with multiple exposures and storing the mean image in 'capture'
    for i in range(1):
        capture = cam.single_exposure(exposure_time=0.3)
        ts = time.time() - t0
        fn = os.path.join(folder,'image_cap_%04d'%(i) + str(ts) + 'img.png')
        plt.imsave(fn,capture)

    # Closing the camera
    cam.close()


# This condition checks if the script is being run directly or imported. If run directly, the code block under this condition will run.
if __name__ == '__main__':
    # Creating an instance of Camera
    live_time_lapse()

