import time
import numpy as np
import clr
import sys
import matplotlib.pyplot as plt

# Add Reference
assembly_path = r"C:\Users\ob303\OneDrive - University of Cambridge\Admin_work\Facilities & Labs\PS\Spectrometer\64bit\DeveloperTools\DLL&Driver"
sys.path.append(assembly_path)
clr.AddReference("HSSUSB2A")

from HSSUSB2_DLL import *

IMAGE_HEADER_SIZE = 256
DATA_COUNT_MAX_VALUE = 1
DATA_TRANSMIT_COUNT = 1
FRAME_COUNT = 1
EXPOSURE_TIME = 20000
CYCLE_TIME = 210000
REPEAT_COUNT = 5


class E_CAPTUREMODE:
    D_CAPTUREMODE_COUNT = 0x00000000
    D_CAPTUREMODE_CONTINUOUS = 0x00000001
    D_CAPTUREMODE_TRIGGER = 0x00000002


class E_GAINMODE:
    D_GAINMODE_SENSOR = 0x00000000
    D_GAINMODE_CIRCUIT = 0x00000001


class E_SENSORGAINMODE:
    D_SENSORGAINMODE_LOWGAIN = 0x00000000
    D_SENSORGAINMODE_HIGHGAIN = 0x00000001
    D_SENSORGAINMODE_NOTHING = 0x000000FF


def Measurement(USB_Device=HSSUSB2()):
    # Initialize Variables
    device_list = [0, 0, 0, 0, 0, 0, 0, 0]
    i_new = 0
    i_old = 0
    mode_gain = E_GAINMODE.D_GAINMODE_SENSOR
    mode_sensor = E_SENSORGAINMODE.D_SENSORGAINMODE_LOWGAIN
    n_cycles = 10
    n_captured = 0
    n_device = 0
    n_data = DATA_COUNT_MAX_VALUE
    n_frames = FRAME_COUNT
    n_transmit = DATA_TRANSMIT_COUNT
    size_x = 0
    size_y = 0
    size_image = 0
    size_data = 0
    spectro_info = Usb2Struct.CSpectroInformation()
    usb_return = 0
    usb_number = 0

    # Start Measurement
    print("Starting Measurement ............")

    # Check Input
    if USB_Device == None:
        print("Wrong Input!")
        return Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__

    # Initialize Device
    usb_return = USB_Device.USB2_initialize()
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Initialize!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Get Connected Device List
    usb_return, n_device = USB_Device.USB2_getModuleConnectionList(device_list, usb_number)
    print("In Total {} Devices".format(n_device))
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Get Device List!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Set Connected Device ID
    DeviceID = device_list[0]

    # Get Device Spectro Information
    usb_return = USB_Device.USB2_getSpectroInformation(DeviceID, spectro_info)[0]
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Get Spectro Information!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Get Device Cooling Type
    CoolingType = spectro_info.unit
    print("Cooling Type: {}".format(CoolingType))

    # Open Device
    usb_return = USB_Device.USB2_open(DeviceID)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Open Device {}!!".format(usb_return, DeviceID))
        print("Exiting ............")
        return usb_return

    # Set Device Capture Mode
    usb_return = USB_Device.USB2_setCaptureMode(DeviceID, E_CAPTUREMODE.D_CAPTUREMODE_COUNT)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Capture Mode!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Set Maximum Data Size
    usb_return = USB_Device.USB2_setDataCount(DeviceID, n_data)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Data Limit!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Set Maximum Transmit Size
    usb_return = USB_Device.USB2_setDataTransmit(DeviceID, n_transmit)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Transmit Limit!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Set Cycle Time
    usb_return = USB_Device.USB2_setExposureCycle(DeviceID, CYCLE_TIME)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Cycle Time!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Set Exposure Time
    usb_return = USB_Device.USB2_setExposureTime(DeviceID, EXPOSURE_TIME)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Exposure Time!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Set Gain Value
    usb_return = USB_Device.USB2_setGain(DeviceID, mode_gain, mode_sensor)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Gain Value!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Get Image Size
    usb_return, size_x, size_y = USB_Device.USB2_getImageSize(DeviceID, size_x, size_y)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Set Image Size!".format(usb_return))
        print("Exiting ............")
        return usb_return
    size_image = size_x * size_y

    # Allocate Buffer
    usb_return = USB_Device.USB2_allocateBuffer(DeviceID, n_frames)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Allocate Buffer!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Start Capture
    print("Starting Capture ............")
    usb_return = USB_Device.USB2_captureStart(DeviceID, n_frames)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Start Capture!".format(usb_return))
        print("Exiting ............")
        return usb_return
    print("Image Data:")

    # Loop Capture
    for i in range(n_cycles):

        # Get Capture Status
        usb_return, n_captured, i_new = USB_Device.USB2_getCaptureStatus(DeviceID, n_captured, i_new)
        time.sleep(1e-2)

        # Successful Capture
        if usb_return == Usb2Struct.Cusb2Err.usb2Success.value__:

            # print(usb_return, n_captured, i_new)

            # Calculate Old Index
            if n_captured > i_new + 1:
                i_old = FRAME_COUNT - (n_captured - (i_new + 1))
            else:
                i_old = (i_new - n_captured) + 1

            # Allocate A Header Buffer
            ImageHeaders = [0] * (IMAGE_HEADER_SIZE * n_captured)
            if ImageHeaders == None:
                return Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__

            # Allocate A Data Buffer
            size_data = n_captured * n_transmit * size_image
            ImageData = [0] * size_data
            if ImageData == None:
                return Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__

            # Allocate A Time Buffer
            ImageTime = [0] * n_transmit * n_captured
            if ImageTime == None:
                return Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__

            # Get Data
            usb_return, ImageHeaders, ImageData, ImageTime = USB_Device.USB2_getImageHeaderData(DeviceID, ImageHeaders,
                                                                                                ImageData, i_old,
                                                                                                n_captured, ImageTime)

            # Display Data
            Display_Data(ImageData)
            data = np.array(ImageData)
            print(data)
            plt.plot(np.linspace(950,1700,len(data)),data)
            plt.show()

            # Stop Capture
            print("Stopping Capture ............")
            usb_return = USB_Device.USB2_captureStop(DeviceID)
            if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
                print("Error code 0x{:04x}: Cannot Stop Capture!".format(usb_return))
                print("Exiting ............")
                return usb_return

            # Next Capture
            if i < n_cycles - 1:
                print("Starting Capture ............")
                usb_return = USB_Device.USB2_captureStart(DeviceID, n_frames)
                if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
                    print("Error code 0x{:04x}: Cannot Start Capture!".format(usb_return))
                    print("Exiting ............")
                    return usb_return

        # Unsuccessful Capture
        else:
            # print(".", end="")
            continue

    # Finish Capture
    if usb_return == Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__:
        return Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__

    # Release Buffer
    print("Releasing Buffer ............")
    usb_return = USB_Device.USB2_releaseBuffer(DeviceID)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Release Buffer!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Close Device
    usb_return = USB_Device.USB2_close(DeviceID)
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Close Device!".format(usb_return))
        print("Exiting ............")
        return usb_return

    # Uninitialize Device
    usb_return = USB_Device.USB2_uninitialize()
    if usb_return != Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Error code 0x{:04x}: Cannot Uninitialize!".format(usb_return))
        print("Exiting ............")
        return usb_return

    return Usb2Struct.Cusb2Err.usb2Success.value__


def Display_Data(ImageData=[]):
    # Display Data
    for i in range(len(ImageData)):
        print("0x{:04x}".format(ImageData[i]), end=" ")
    print()

    return True


if __name__ == "__main__":

    # Initialize Device
    USB_Device = HSSUSB2()

    # Start Measurement
    usb_return = Measurement(USB_Device)

    # Display Result
    if usb_return == Usb2Struct.Cusb2Err.usb2Success.value__:
        print("Measurement Finished!")
    elif usb_return == Usb2Struct.Cusb2Err.usb2Err_unsuccess.value__:
        print("Measurement Terminated!")
    else:
        print("Measurement Finished with Error Code 0x{:04x}".format(usb_return))
