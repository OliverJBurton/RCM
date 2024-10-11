# Import necessary libraries
import time  # Provides time-related functions
import numpy as np  # Provides support for large, multi-dimensional arrays and matrices
import clr  # Provides support for calling .NET code from Python
import sys  # Provides access to system-specific parameters and functions
import matplotlib.pyplot as plt  # Provides plotting functionality for data visualization

# Add reference to the external assembly (DLL) for interfacing with the spectrometer.
# The path where the DLL is located is added to the system path.
assembly_path = r"C:\Users\ob303\OneDrive - University of Cambridge\Admin_work\Facilities & Labs\PS\Spectrometer\64bit\DeveloperTools\DLL&Driver"
sys.path.append(assembly_path)
clr.AddReference("HSSUSB2A")  # Add reference to the DLL for spectrometer control.

# Import necessary functions and structures from the DLL.
from HSSUSB2_DLL import *

# Constants for image and data handling.
IMAGE_HEADER_SIZE = 256  # Size of the image header.
DATA_COUNT_MAX_VALUE = 1  # Maximum value for data count.
DATA_TRANSMIT_COUNT = 1  # Number of data transmit cycles.
FRAME_COUNT = 1  # Number of frames per capture.
EXPOSURE_TIME = 20000  # Exposure time for the spectrometer (in microseconds).
CYCLE_TIME = 210000  # Cycle time between exposures.
REPEAT_COUNT = 5  # Number of times to repeat the measurement.

# Enumeration class for different capture modes in the spectrometer.
class E_CAPTUREMODE:
    D_CAPTUREMODE_COUNT = 0x00000000  # Single capture mode.
    D_CAPTUREMODE_CONTINUOUS = 0x00000001  # Continuous capture mode.
    D_CAPTUREMODE_TRIGGER = 0x00000002  # Triggered capture mode.

# Enumeration class for different gain modes.
class E_GAINMODE:
    D_GAINMODE_SENSOR = 0x00000000  # Sensor gain mode.
    D_GAINMODE_CIRCUIT = 0x00000001  # Circuit gain mode.

# Enumeration class for different sensor gain modes.
class E_SENSORGAINMODE:
    D_SENSORGAINMODE_LOWGAIN = 0x00000000  # Low gain mode for the sensor.
    D_SENSORGAINMODE_HIGHGAIN = 0x00000001  # High gain mode for the sensor.
    D_SENSORGAINMODE_NOTHING = 0x000000FF  # No gain applied.

# Main function to perform the spectrometer measurement.
def Measurement(USB_Device=HSSUSB2()):
    """
    Function to perform a measurement using the HSSUSB2 spectrometer.

    Args:
        USB_Device (HSSUSB2): The connected USB device object representing the spectrometer.

    Returns:
        int: The result code from the measurement process (success or error code).
    """

    # Initialize local variables for measurement parameters and device status.
    device_list = [0, 0, 0, 0, 0, 0, 0, 0]  # List to store connected devices.
    i_new = 0  # New index for frame capture.
    i_old = 0  # Old index for frame capture.
    mode_gain = E_GAINMODE.D_GAINMODE_SENSOR  # Set gain mode to sensor gain.
    mode_sensor = E_SENSORGAINMODE.D_SENSORGAINMODE_LOWGAIN  # Set sensor gain mode to low gain.
    n_cycles = 10  # Number of capture cycles.
    n_captured = 0  # Number of captured frames.
    n_device = 0  # Number of connected devices.
    n_data = DATA_COUNT_MAX_VALUE  # Maximum data count.
    n_frames = FRAME_COUNT  # Number of frames to capture.
    n_transmit = DATA_TRANSMIT_COUNT  # Number of data transmissions.
    size_x = 0  # X dimension of the image.
    size_y = 0  # Y dimension of the image.
    size_image = 0  # Total image size (pixels).
    size_data = 0  # Size of the data buffer.
    spectro_info = Usb2Struct.CSpectroInformation()  # Object to store spectro information.
    usb_return = 0  # Variable to store return codes from USB functions.
    usb_number = 0  # USB device number.

    # Begin the measurement process.
    print("Starting Measurement ............")

    # Check if the USB device is properly initialized.
    if USB_Device == None:
        print("Wrong Input!")
        return Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__

    # Initialize the USB device.
    usb_return = USB_Device.USB2_initialize()
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Initialize!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Get the list of connected devices.
    usb_return, n_device = USB_Device.USB2_getModuleConnectionList(device_list, usb_number)
    print("In Total {} Devices".format(n_device))
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Get Device List!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Set the connected device ID (first device in the list).
    DeviceID = device_list[0]

    # Retrieve information about the spectrometer.
    usb_return = USB_Device.USB2_getSpectroInformation(DeviceID, spectro_info)[0]
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Get Spectro Information!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Get the device's cooling type.
    CoolingType = spectro_info.unit
    print("Cooling Type: {}".format(CoolingType))

    # Open the connection to the spectrometer device.
    usb_return = USB_Device.USB2_open(DeviceID)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Open Device {}!!".format(usb_return, DeviceID))
        print("Exiting ............")
        return usb_return

    # Set the device's capture mode to "count" mode.
    usb_return = USB_Device.USB2_setCaptureMode(DeviceID, E_CAPTUREMODE.D_CAPTUREMODE_COUNT)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Capture Mode!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Set the maximum data size for the device.
    usb_return = USB_Device.USB2_setDataCount(DeviceID, n_data)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Data Limit!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Set the maximum transmit size for the device.
    usb_return = USB_Device.USB2_setDataTransmit(DeviceID, n_transmit)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Transmit Limit!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Set the exposure cycle time.
    usb_return = USB_Device.USB2_setExposureCycle(DeviceID, CYCLE_TIME)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Cycle Time!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Set the exposure time for the device.
    usb_return = USB_Device.USB2_setExposureTime(DeviceID, EXPOSURE_TIME)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Exposure Time!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Set the gain value for the device.
    usb_return = USB_Device.USB2_setGain(DeviceID, mode_gain, mode_sensor)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Gain Value!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Get the image size for the device.
    usb_return, size_x, size_y = USB_Device.USB2_getImageSize(DeviceID, size_x, size_y)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Image Size!".format(usb_return))
        print("Exiting ............")
        return usb_return
    size_image = size_x * size_y  # Calculate total image size.

    # Allocate buffer for the image data.
    usb_return = USB_Device.USB2_allocateBuffer(DeviceID, n_frames)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Allocate Buffer!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Start capturing image data.
    print("Starting Capture ............")
    usb_return = USB_Device.USB2_captureStart(DeviceID, n_frames)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Start Capture!".format(usb_return))
        print("Exiting ............")
        return usb_return
    print("Image Data:")

    # Loop through capture cycles.
    for i in range(n_cycles):

        # Get the capture status from the device.
        usb_return, n_captured, i_new = USB_Device.USB2_getCaptureStatus(DeviceID, n_captured, i_new)
        time.sleep(1e-2)  # Wait briefly between captures.

        # If the capture was successful, proceed with data processing.
        if usb_return == Usb2Struct.Cusb2Err.usb2Success.value__:

            # Calculate the old index for the frame capture.
            if n_captured > i_new + 1:
                i_old = FRAME_COUNT - (n_captured - (i_new + 1))
            else:
                i_old = (i_new - n_captured) + 1

            # Allocate a buffer for the image headers.
            ImageHeaders = [0] * (IMAGE_HEADER_SIZE * n_captured)
            if ImageHeaders == None:
                return Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__

            # Allocate a buffer for the image data.
            size_data = n_captured * n_transmit * size_image
            ImageData = [0] * size_data
            if ImageData == None:
                return Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__

            # Allocate a buffer for the image time.
            ImageTime = [0] * n_transmit * n_captured
            if ImageTime == None:
                return Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__

            # Retrieve the image data from the device.
            usb_return, ImageHeaders, ImageData, ImageTime = USB_Device.USB2_getImageHeaderData(
                DeviceID, ImageHeaders, ImageData, i_old, n_captured, ImageTime
            )

            # Display the captured data.
            Display_Data(ImageData)

            # Convert the data to a NumPy array and plot it.
            data = np.array(ImageData)
            print(data)
            plt.plot(np.linspace(950, 1700, len(data)), data)
            plt.show()

            # Stop the capture process.
            print("Stopping Capture ............")
            usb_return = USB_Device.USB2_captureStop(DeviceID)
            if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
                print("Error code 0x{:04x}: Cannot Stop Capture!".format(usb_return))
                print("Exiting ............")
                return usb_return

            # If there are more capture cycles, start the next capture.
            if i < n_cycles - 1:
                print("Starting Capture ............")
                usb_return = USB_Device.USB2_captureStart(DeviceID, n_frames)
                if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
                    print("Error code 0x{:04x}: Cannot Start Capture!".format(usb_return))
                    print("Exiting ............")
                    return usb_return

        # If the capture was unsuccessful, retry.
        else:
            continue

    # If the measurement finished unsuccessfully, return the error code.
    if usb_return == Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__:
        return Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__

    # Release the buffer after the capture process.
    print("Releasing Buffer ............")
    usb_return = USB_Device.USB2_releaseBuffer(DeviceID)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Release Buffer!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Close the device after the measurement is completed.
    usb_return = USB_Device.USB2_close(DeviceID)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Close Device!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Uninitialize the device and release resources.
    usb_return = USB_Device.USB2_uninitialize()
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Uninitialize!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Return the success code.
    return Usb2Struct.Cusb2Err.usb2Success.value__

# Function to display the data in a readable format.
def Display_Data(ImageData=[]):
    """
    Displays the image data captured from the spectrometer.

    Args:
        ImageData (list): The image data to be displayed.
    """
    for i in range(len(ImageData)):
        print("0x{:04x}".format(ImageData[i]), end=" ")
    print()
    return True

if __name__ == "__main__":
    """
    Main program to initialize the USB device and perform the measurement.
    """

    # Create an instance of the HSSUSB2 device.
    USB_Device = HSSUSB2()

    # Start the measurement process.
    usb_return = Measurement(USB_Device)

    # Display the result of the measurement.
    if usb_return == Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Measurement Finished!")
    elif usb_return == Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__:
        print("Measurement Terminated!")
    else:
        print("Measurement Finished with Error Code 0x{:04x}".format(usb_return))
