# First, we import the matplotlib library, which is useful for creating static, animated, and interactive visualizations in Python.
import matplotlib.pyplot as plt
import os
import time

# Importing the Thorlabs device library from the pylablib, which is a Python library for control and data acquisition in scientific experiments.
from pylablib.devices import Thorlabs as tl
import pylablib as pll

# Setting the path for the Thorlabs DLL used for camera communication
pll.par["devices/dlls/uc480"] = r"C:/Program Files/Thorlabs/Scientific Imaging/ThorCam"

# NumPy is a Python library used for working with arrays. It also has functions for working in the domain of linear algebra, Fourier transform, and matrices.
import numpy as np


class Camera_HS():
    """
    A class to interact with a high-speed Thorlabs camera. This class handles camera initialization,
    capturing images, and managing exposure settings.
    """

    def __init__(self):
        """
        Initializes the Camera_HS class by opening a connection to the first camera found,
        setting the region of interest (ROI), and configuring exposure settings.
        """
        # List all connected cameras and print the serial number of the first camera.
        print('Camera Serial : ', tl.list_cameras_tlcam())

        # Open the first camera found using its serial number.
        self.cam = tl.ThorlabsTLCamera(serial='24070')

        # Open the camera for use.
        self.cam.open()

        # Set the camera's region of interest (ROI), which defines the area captured by the sensor.
        self.cam.set_roi(0, 4096, 0, 2616)

        # Verify and print whether the camera was successfully opened.
        print('Camera opened : ', self.cam.is_opened())

        # Initialize the camera's pixel range with min and max values.
        self.max_val = 4096
        self.min_val = 0

        # Set an initial exposure time of 15 milliseconds.
        self.exposure = 15  # ms

        # Apply the initial exposure time to the camera.
        self.cam.set_exposure(self.exposure)

    def single_exposure(self, exposure_time=1):
        """
        Captures a single image with the given exposure time.

        :param exposure_time: The exposure time in milliseconds (default is 1 ms).
        :return: The captured image as a NumPy array of type uint16.
        """
        # Set the camera exposure time.
        self.cam.set_exposure(exposure_time)
        # Capture a single image and convert it to a NumPy array of type uint16.
        return self.cam.snap().astype(np.uint16)

    def average_exposure(self, exposure_time=1, averages=5):
        """
        Captures multiple images with the specified exposure time and returns the average.

        :param exposure_time: The exposure time in milliseconds (default is 1 ms).
        :param averages: Number of images to capture and average (default is 5).
        :return: The averaged image as a NumPy array.
        """
        self.cam.set_exposure(exposure_time)
        # Initialize an empty list to store the captured images.
        exps = []
        # Capture the specified number of images.
        for i in range(averages):
            exps.append(self.cam.snap().astype(np.uint16))
        # Return the mean of all captured images.
        return np.mean(exps, axis=0)

    def multi_exposure(self, start_exposure=1e-4, doubles=10, discard_ratio=0.2):
        """
        Captures multiple images with exposure times that double sequentially,
        and combines them into a single image while discarding over/under-exposed pixels.

        :param start_exposure: Initial exposure time in seconds (default is 0.0001 s).
        :param doubles: Number of times the exposure is doubled (default is 10).
        :param discard_ratio: The percentage of extreme pixel values to discard (default is 0.2).
        :return: The mean image after processing multiple exposures.
        """
        # Initialize a list to store the raw captured data.
        raw_data = []
        # Loop through the exposure steps, doubling each time.
        for i in range(doubles):
            # Set the current exposure time.
            self.cam.set_exposure(start_exposure * 2 ** i)
            # Capture an image and convert it to a NumPy array of type float32.
            temp = self.cam.snap().astype(np.float32)
            # Discard pixels that are too bright (above the discard threshold).
            temp[temp >= self.max_val * (1 - discard_ratio)] = np.NaN
            # Discard pixels that are too dark (below the discard threshold).
            temp[temp <= self.max_val * discard_ratio] = np.NaN
            # Normalize the image by dividing by the exposure ratio and add to the list.
            raw_data.append(temp / (2 ** i))

        # Convert the list of raw data to a NumPy array.
        raw_data = np.array(raw_data)
        # Calculate the mean of the images, ignoring NaN values.
        mean_data = np.nanmean(raw_data, axis=0)
        # Return the processed mean image.
        return mean_data

    def close(self):
        """
        Closes the camera connection. This method should be called after finishing camera operations.
        """
        self.cam.close()


class Camera_BA():
    """
    A class to interact with another Thorlabs camera (different model).
    Similar functionality to Camera_HS but specific to this particular camera's parameters.
    """

    def __init__(self):
        """
        Initializes the Camera_BA class by opening a connection to the first camera found,
        setting the region of interest (ROI), and configuring exposure settings.
        """
        print('Camera Serial : ', tl.list_cameras_tlcam())
        self.cam = tl.ThorlabsTLCamera(serial='23588')
        self.cam.open()
        self.cam.set_roi(0, 4096, 0, 2616)
        print('Camera opened : ', self.cam.is_opened())
        self.max_val = 4096
        self.min_val = 0
        self.exposure = 50  # ms
        self.cam.set_exposure(self.exposure)

    def single_exposure(self, exposure_time=1, timeout=500e-3):
        """
        Captures a single image with the given exposure time and optional timeout.

        :param exposure_time: The exposure time in milliseconds (default is 1 ms).
        :param timeout: Timeout period in seconds (default is 0.5 s).
        :return: The captured image as a NumPy array.
        """
        self.cam.set_exposure(exposure_time)
        return self.cam.snap(timeout=timeout)

    def average_exposure(self, exposure_time=1, averages=5):
        """
        Captures multiple images with the specified exposure time and returns the average.

        :param exposure_time: The exposure time in milliseconds (default is 1 ms).
        :param averages: Number of images to capture and average (default is 5).
        :return: The averaged image as a NumPy array.
        """
        self.cam.set_exposure(exposure_time)
        exps = []
        for i in range(averages):
            exps.append(self.cam.snap())
        return np.mean(exps, axis=0)

    def multi_exposure(self, start_exposure=1e-4, doubles=10, discard_ratio=0.2):
        """
        Captures multiple images with exposure times that double sequentially,
        and combines them into a single image while discarding over/under-exposed pixels.

        :param start_exposure: Initial exposure time in seconds (default is 0.0001 s).
        :param doubles: Number of times the exposure is doubled (default is 10).
        :param discard_ratio: The percentage of extreme pixel values to discard (default is 0.2).
        :return: The mean image after processing multiple exposures.
        """
        raw_data = []
        for i in range(doubles):
            self.cam.set_exposure(start_exposure * 2 ** i)
            temp = self.cam.snap().astype(np.float32)
            temp[temp >= self.max_val * (1 - discard_ratio)] = np.NaN
            temp[temp <= self.max_val * discard_ratio] = np.NaN
            raw_data.append(temp / (2 ** i))
        raw_data = np.array(raw_data)
        mean_data = np.nanmean(raw_data, axis=0)
        return mean_data

    def close(self):
        """
        Closes the camera connection. This method should be called after finishing camera operations.
        """
        self.cam.close()


def live_time_lapse():
    """
    Captures a time-lapse of images from the Camera_HS and saves them as PNG files in a specified folder.
    """
    folder = r'C:\Users\ob303\OneDrive - University of Cambridge\Projects_current\Experimental\2023_OxideNanowires\LinkhamStageTest_640nmW'

    # Create an instance of Camera_HS to interact with the high-speed camera.
    cam = Camera_HS()
    t0 = time.time()

    # Capture images in a time-lapse loop.
    for i in range(1):
        capture = cam.single_exposure(exposure_time=0.3)
        ts = time.time() - t0
        fn = os.path.join(folder, 'image_cap_%04d' % (i) + str(ts) + 'img.png')
        plt.imsave(fn, capture)

    # Close the camera connection after capturing images.
    cam.close()


# If this script is being run directly, capture and display an image using Camera_HS.
if __name__ == '__main__':
    cam = Camera_HS()
    arr = cam.single_exposure(10e-3)
    plt.imshow(arr)
    plt.show()
