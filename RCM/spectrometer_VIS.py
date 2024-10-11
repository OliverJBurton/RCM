# Import necessary libraries
from oceandirect.OceanDirectAPI import OceanDirectAPI, OceanDirectError, FeatureID  # Import OceanDirect API for spectrometer control
import matplotlib.pyplot as plt  # Import for plotting data

# Spectrometer control script to input gain, exposure time, and repeats to return counts vs wavelength

# Note: The product manual contains detailed explanations of error codes in Appendix A.
# https://www.oceanoptics.com/wp-content/uploads/2024/05/MNL-1025-OceanDirect-User-Manual-060822.pdf

class Ocean_Spectrometer(OceanDirectAPI):
    """
    A class to control and interface with an Ocean Optics spectrometer using the OceanDirectAPI.

    This class handles initialization, device setup, spectrum reading, and device shutdown.
    """

    def __init__(self):
        """
        Initializes the Ocean_Spectrometer class, detects connected spectrometers, and opens the first available device.

        Raises:
            RuntimeError: If no spectrometers are found.
        """
        # Initialize the parent OceanDirectAPI class.
        super().__init__()

        try:
            # Find connected USB spectrometer devices.
            device_count = self.find_usb_devices()

            # If no devices are found, raise an error.
            if device_count == 0:
                raise RuntimeError("No ocean spectroscopes found")

            # Get the list of device IDs for the detected devices.
            device_ids = self.get_device_ids()
            print("Device id: ", device_ids)

            # If more than one device is found, use the first one.
            if device_count > 1:
                print("More than 1 device detected, selecting first device")

            # Open the first detected device and store its ID and serial number.
            self.device_id = device_ids[0]
            self.device = self.open_device(self.device_id)
            self.serial_number = self.device.get_serial_number()

            # Print the serial number of the initialized device.
            print(f"Device with serial number {self.serial_number} has been initialised.")

        # Catch any errors that occur during initialization and display the error code and message.
        except OceanDirectError as err:
            [errorCode, errorMsg] = err.get_error_details()
            print(f"Ocean_Spectrometer initialisation has failed: {errorCode} | {errorMsg}")

    def close_device(self):
        """
        Closes the connection to the spectrometer and shuts down the API.

        This method should be called when the device is no longer needed to properly release resources.
        """
        # Close the device using its ID and shut down the API.
        self.close_device(self.device_id)
        self.shutdown()

    def read_spectra(self, exposure_time_Us: int, num_average: int):
        """
        Reads the spectrum from the spectrometer.

        Args:
            exposure_time_Us (int): The exposure time in microseconds for capturing the spectrum.
            num_average (int): The number of scans to average for the final spectrum.

        Returns:
            tuple: A tuple containing two lists - wavelengths and corresponding spectra data (counts).

        Raises:
            OceanDirectError: If there is an error during spectrum acquisition.

        Note:
            The integration time defines the duration light is allowed to pass into the spectrometer's detector.
            Setting the exposure too high can lead to saturation, while setting it too low may result in insufficient signal.
        """
        try:
            # Set the integration (exposure) time for the spectrometer in microseconds.
            self.device.set_integration_time(exposure_time_Us)

            # Set the number of scans to average.
            self.device.set_scans_to_average(num_average)

            # Retrieve the wavelengths measured by the spectrometer.
            wavelengths = self.device.get_wavelengths()

            # Retrieve the spectrum data (counts) from the spectrometer.
            spectra = self.device.get_formatted_spectrum()

            # Return the wavelengths and spectra data.
            return wavelengths, spectra

        # Catch and display any errors that occur during spectrum reading.
        except OceanDirectError as err:
            [errorCode, errorMsg] = err.get_error_details()
            print(f"Ocean_Spectrometer.read_spectra() exception: {errorCode} | {errorMsg}")


if __name__ == "__main__":
    """
    Main function to initialize the Ocean spectrometer, read the spectra, and plot the results.

    This section sets the exposure time and averaging parameters for the spectrometer and plots the resulting spectra.
    """
    # Initialize the Ocean spectrometer device.
    device = Ocean_Spectrometer()

    # Read the spectra with an exposure time of 100,000 microseconds and 5 scans to average.
    wavelengths, output = device.read_spectra(100000, 5)

    # Plot the resulting spectra (counts vs. wavelengths).
    plt.plot(wavelengths, output)
    plt.xlabel("Wavelengths (nm)")
    plt.ylabel("Counts")
    plt.show()
