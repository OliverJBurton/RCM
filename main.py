# Import necessary modules
import sys  # Provides system-specific parameters and functions
sys.path.append('../RCM/RCM')  # Append the path for custom modules

# Import other libraries and custom modules
import numpy as np  # For array handling and numerical computations
import matplotlib.pyplot as plt  # For plotting images and graphs
from camera import Camera_HS  # High-speed camera interface
from camera import Camera_BA  # Baseline camera interface
from light import DC2200  # LED controller interface
from stage import Controller  # Stage controller interface
from tunablefilter import TunableFilter  # Tunable filter control interface
import time  # For time delays and time management
import os  # For file and directory operations
import cv2  # OpenCV for image processing
import imageio  # For writing image files



class FullControlMicroscope:
    """
    A class to manage and control a microscope system that integrates multiple hardware components:
    - High-speed camera (Camera_HS)
    - LED light source (DC2200)
    - Motorized stage (Controller)
    - Tunable filter (TunableFilter)

    This class provides functions to control each component and capture data from the system.
    """

    def __init__(self):
        """
        Initializes and connects all the peripherals (cameras, LED, stage, tunable filter) required for microscope control.
        """
        # Initialize the high-speed camera
        self.chs = Camera_HS()
        print('HS camera connected')

        # Uncomment the following lines if the Baseline camera (Camera_BA) is used
        # self.cba = Camera_BA()
        # print('TL camera connected')

        # Initialize the LED light source
        self.led = DC2200()
        print('LS connected')

        # Initialize the motorized stage, connecting to the specified COM port
        self.sta = Controller(which_port='COM4',
                              stages=('ZFM2030', 'ZFM2030', 'ZFM2030'),  # Define stage types for each axis
                              reverse=(False, False, True),  # Reverse direction of the Z-axis
                              verbose=True,  # Enable verbose output
                              very_verbose=False)  # Disable very verbose output
        print('Stage connected')

        # Initialize the tunable filter
        self.lcf = TunableFilter()
        print('LC connecting...')
        self.lcf.open()  # Open connection to the tunable filter
        print('LC connected')

    def close(self):
        """
        Closes all peripherals and releases resources.

        This function ensures that all connected devices (cameras, LED, stage, and tunable filter) are properly shut down.
        """
        self.chs.close()  # Close the high-speed camera
        # self.cba.close()  # Uncomment to close the Baseline camera if used
        self.led.close()  # Close the LED controller
        self.sta.close()  # Close the motorized stage
        self.lcf.close()  # Close the tunable filter

    def aquire_HS_datacube(self, wavelength_range=[420, 730], no_spectra=5, exposuretime=[], save_folder=[]):
        """
        Acquires a hyper-spectral datacube using the high-speed camera at different wavelengths controlled by the tunable filter.

        Args:
            wavelength_range (list): The range of wavelengths to capture, in nanometers (default: [420, 730]).
            no_spectra (int): The number of spectral points to capture (default: 5).
            exposuretime (list or int): Exposure time for the camera in milliseconds (default: [] uses the camera's current exposure).
            save_folder (str): Folder to save captured images (default: [] does not save images).

        Returns:
            tuple: A tuple containing the wavelengths and captured images (hypercube) if `save_folder` is not provided.
        """
        step_size = (wavelength_range[1] - wavelength_range[0]) / no_spectra  # Calculate step size for wavelengths
        wavelengths = np.arange(wavelength_range[0], wavelength_range[1], step_size)  # Generate wavelength steps

        # Set exposure time to current camera exposure if not provided
        exposure_time = self.chs.exposure if exposuretime == [] else exposuretime

        wavelengths = []  # List to store wavelengths used
        hypercube = []  # List to store captured images

        # Iterate through the specified wavelength range and capture images
        for wl in np.linspace(wavelength_range[0], wavelength_range[1], no_spectra):
            wavelengths.append(wl)  # Append the wavelength to the list
            self.lcf.set_wavelength(int(wl))  # Set the tunable filter to the current wavelength
            time.sleep(3e-2)  # Small delay to ensure the filter is set
            hypercube.append(self.chs.single_exposure(exposure_time=exposure_time))  # Capture the image

        # Return the data or save images based on the `save_folder` parameter
        if save_folder == []:
            return wavelengths, hypercube
        else:
            for ii, wl in enumerate(wavelengths):
                # Save each captured image to the specified folder
                fn = os.path.join(save_folder, f'image_cap_{ii:04d}_{wl}_img.png')
                imageio.imwrite(fn, hypercube[ii].astype(np.uint16))  # Save image as 16-bit PNG

    def aquire_HS_time_series(self, wavelength_range=[420, 730], no_spectra=5, exposuretime=[], save_folder=[], time_increment=10, total_time=7200):
        """
        Acquires a time-series of hyper-spectral images using the high-speed camera, capturing at regular intervals.

        Args:
            wavelength_range (list): The range of wavelengths to capture, in nanometers (default: [420, 730]).
            no_spectra (int): The number of spectral points to capture at each time step (default: 5).
            exposuretime (list or int): Exposure time for the camera in milliseconds (default: [] uses the camera's current exposure).
            save_folder (str): Folder to save captured images (default: [] does not save images).
            time_increment (int): Time increment between each acquisition in seconds (default: 10).
            total_time (int): Total time duration for the acquisition in seconds (default: 7200 seconds).

        This function captures data at regular time intervals, saving the captured images in the specified folder.
        """
        t0 = time.time()  # Start time
        ti = time.time()  # Current time
        n = 0  # Counter for time steps

        # Loop until the total time is reached
        while ti - t0 < total_time:
            time.sleep(1e-3)  # Small delay to avoid excessive CPU usage
            ti = time.time()  # Update current time

            # Initial immediate capture
            if n==0:
                # Acquire hyperspectral datacube
                wavelengths, hypercube = self.aquire_HS_datacube(wavelength_range=wavelength_range, no_spectra=no_spectra, exposuretime=exposuretime, save_folder=[])

                # Save each captured image
                for ii, wl in enumerate(wavelengths):
                    fn = os.path.join(save_folder, f'image_cap_{n:04d}_{wl}_{ti - t0:.2f}_img.png')
                    imageio.imwrite(fn, hypercube[ii].astype(np.uint16))  # Save image as 16-bit PNG

                n += 1  # Increment the time step counter

            # Capture data at each time increment
            if ti - t0 > time_increment:
                # Acquire hyperspectral datacube
                wavelengths, hypercube = self.aquire_HS_datacube(wavelength_range=wavelength_range, no_spectra=no_spectra, exposuretime=exposuretime, save_folder=[])

                # Save each captured image
                for ii, wl in enumerate(wavelengths):
                    fn = os.path.join(save_folder, f'image_cap_{n:04d}_{wl}_{ti - t0:.2f}_img.png')
                    imageio.imwrite(fn, hypercube[ii].astype(np.uint16))  # Save image as 16-bit PNG

                n += 1  # Increment the time step counter

    def aquire_single_spec_vis(self, exposure_time_Us=100000, num_average=5):
        """
        Captures a single spectrum using the Ocean Optic spectrometer.

        Args:
            exposure_time_Us (int): The exposure time in microseconds for the spectrometer (default: 100000).
            num_average (int): The number of scans to average for the final spectrum (default: 5).

        Returns:
            tuple: A tuple containing the wavelengths and the corresponding spectrum (counts).

        This method uses the Ocean Optic spectrometer to capture a spectrum at the given exposure time.
        """
        # Initialize the spectrometer
        spectrometer = Ocean_Spectrometer()

        # Capture the spectrum
        wavelengths, spectrum = spectrometer.read_spectra(exposure_time_Us=exposure_time_Us, num_average=num_average)

        # Return the captured data
        return wavelengths, spectrum

    def scan_xy_and_acquire_spectra(self, x_step, y_step, x_points, y_points, exposure_time_Us=100000, num_average=5, save_folder=None):
        """
        Moves the stage in X and Y directions relative to the current position over a grid of points and acquires a spectrum at each point.

        Args:
            x_step (float): The step size in micrometers for each move in the X direction.
            y_step (float): The step size in micrometers for each move in the Y direction.
            x_points (int): The number of points to measure in the X direction.
            y_points (int): The number of points to measure in the Y direction.
            exposure_time_Us (int): The exposure time for the spectrometer in microseconds (default: 100000).
            num_average (int): The number of scans to average for the final spectrum (default: 5).
            save_folder (str): The folder to save each spectrum (if provided).

        Returns:
            dict: A dictionary with the (x, y) relative moves as keys and the captured spectra as values.
        """
        # Initialize the spectrometer
        spectrometer = Ocean_Spectrometer()

        # Dictionary to store the spectra at each relative position
        spectra_data = {}

        # Start the scan from the current position
        print("Starting scan...")

        for x_idx in range(x_points):
            for y_idx in range(y_points):
                # Calculate the relative move for the current step
                x_move = x_step * x_idx  # Move in X direction by x_step * x_idx
                y_move = y_step * y_idx  # Move in Y direction by y_step * y_idx

                print(f"Moving relative to current position by X: {x_move:.2f} um, Y: {y_move:.2f} um")

                # Move stage by relative distance in X and Y axes
                self.sta.move_um(0, x_step, relative=True)  # Relative move in X-axis (channel 0)
                self.sta.move_um(1, y_step, relative=True)  # Relative move in Y-axis (channel 1)

                # Acquire the spectrum at the current relative position
                wavelengths, spectrum = spectrometer.read_spectra(exposure_time_Us=exposure_time_Us, num_average=num_average)

                # Store the spectrum in the dictionary with (x_move, y_move) as the key
                spectra_data[(x_move, y_move)] = (wavelengths, spectrum)

                # Optionally save the spectrum as a file
                if save_folder is not None:
                    filename = os.path.join(save_folder, f'spectrum_X{x_move:.2f}_Y{y_move:.2f}.csv')
                    data = np.column_stack((wavelengths, spectrum))
                    np.savetxt(filename, data, delimiter=',', header='Wavelength, Spectrum', comments='')

                print(f"Spectrum acquired at relative X: {x_move:.2f} um, Y: {y_move:.2f} um")

            # Move back to the starting Y position after finishing the Y moves for the current X position
            self.sta.move_um(1, -y_step * y_points, relative=True)  # Reset Y to start of row

        # Return the collected spectra
        return spectra_data


if __name__ == '__main__':
    """
    Main entry point for testing the FullControlMicroscope class.

    The script initializes the microscope, acquires a datacube, and then closes the connection to the peripherals.
    """

    fo = r'D:\OB303\data\2025_20250121AuMix_LAP3_CKMYborder_v2'
    # Initialize the FullControlMicroscope class
    msc = FullControlMicroscope()

    # Acquire a hyperspectral datacube
    msc.aquire_HS_time_series(wavelength_range=[450, 720], no_spectra=21, exposuretime=100e-3, save_folder=fo, time_increment=150, total_time=10000000)

    # Close all devices and peripherals
    msc.close()
