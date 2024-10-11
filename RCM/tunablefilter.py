# Import necessary libraries
import re  # For regular expressions
import time  # For sleep function (used in loops to introduce delays)
from KURIOS_COMMAND_LIB import *  # Import commands for controlling the KURIOS tunable filter

def GetDeviceSNCN(IDStr):
    """
    Extracts the serial number (SN) and controller number (CN) from a device identification string.

    Args:
        IDStr (str): The device ID string containing both SN and CN.

    Returns:
        tuple: A tuple containing the serial number (SN) and controller number (CN) as strings.
    """
    SNpattern = re.compile('SN(\d{1,10})')  # Regular expression to find the serial number
    SNum = re.findall(SNpattern, IDStr)  # Find all matches for SN

    CNpattern = re.compile('CN(\d{1,10})')  # Regular expression to find the controller number
    CNum = re.findall(CNpattern, IDStr)  # Find all matches for CN

    return SNum[0], CNum[0]  # Return the first match for both SN and CN


def GetDeviceOpticalHeadTypeNumber(hex_string, target_dict, max_length=4):
    """
    Converts a hexadecimal string to binary and matches it with the corresponding feature in the dictionary.

    Args:
        hex_string (str): The hexadecimal string representing the optical head type.
        target_dict (dict): A dictionary mapping binary positions to optical head types.
        max_length (int): The maximum length to process in the binary string.

    Returns:
        list: A list of matched optical head types based on the input binary string.
    """
    try:
        bin_str = bin(ord(hex_string))  # Convert the hex string to binary
    except Exception as e:
        raise Exception(f'transfer hex {hex_string} to bin error! {e}')

    pattern = re.compile('0b(\d*)')  # Regular expression to extract the binary digits
    bin_val = pattern.findall(bin_str)[0]  # Extract the binary string
    bin_val_reverse = bin_val[::-1]  # Reverse the binary string for easier indexing

    target_ls = []
    for t in range(len(bin_val_reverse)):
        if t < max_length and t in target_dict.keys():
            if bin_val_reverse[t] == '1':
                target_ls.append(target_dict[t])
    return target_ls  # Return the matched features from the binary string


def CommonFunc(serialNumber):
    """
    Common initialization function for the Kurios device, retrieving device status, temperature, and specifications.

    Args:
        serialNumber (str): The serial number of the device to open.

    Returns:
        int: The handle for the opened device (hdl) if successful, otherwise returns -1.
    """
    hdl = KuriosOpen(serialNumber, 115200, 3)  # Open the device with specified baud rate and timeout
    if hdl < 0:
        print("Connect ", serialNumber, "fail")
        return -1
    else:
        print("Connect ", serialNumber, "successful")

    # Check if the device is open
    result = KuriosIsOpen(serialNumber)
    print("KuriosIsOpen ", result)

    # Retrieve device ID information
    id = []
    result = KuriosGetId(hdl, id)
    if result < 0:
        print("KuriosGetId fail ", result)
    else:
        print(id)
        IDString = id
        for s in IDString:
            SN, CN = GetDeviceSNCN(s)
            print("SN: ", SN, "CN: ", CN)
        if (int(SN) >= 212254) and (int(SN) != int(CN)):
            print("KURIOS optical head SN# and controller CN# do not match. It is recommended to use matched optical head and controller for optimum factory calibrated performance.")

    # Get device status
    DeviceStatus = [0]
    DeviceStatusList = {0: 'initialization', 1: 'warm up', 2: 'ready'}
    result = KuriosGetStatus(hdl, DeviceStatus)
    if result < 0:
        print("Get device status fail", result)
    else:
        print("Get device status:", DeviceStatusList.get(DeviceStatus[0]))

    # Get device temperature
    DeviceTem = [0]
    result = KuriosGetTemperature(hdl, DeviceTem)
    if result < 0:
        print("Get device Temperature fail", result)
    else:
        print("Get device Temperature:", DeviceTem)

    # Get device wavelength specification
    MaxWavelength = [0]
    MinWavelength = [0]
    result = KuriosGetSpecification(hdl, MaxWavelength, MinWavelength)
    if result < 0:
        print("KuriosGetSpecification fail ", result)
    else:
        print("MaxWavelength: ", MaxWavelength, "MinWavelength: ", MinWavelength)

    # Get optical head type and bandwidth mode
    SpectrumRange = [0]
    SpectrumRangeList = {0: 'Visible', 1: 'NIR'}
    BandwidthMode = [0]
    BandwidthModeList = {0: 'BLACK', 1: 'WIDE', 2: 'MEDIUM', 3: 'NARROW'}
    result = KuriosGetOpticalHeadType(hdl, SpectrumRange, BandwidthMode)
    if result < 0:
        print("KuriosGetOpticalHeadType fail ", result)
    else:
        print("filterSpectrumRange: ", GetDeviceOpticalHeadTypeNumber(SpectrumRange[1], SpectrumRangeList),
              "availableBandwidthMode: ", GetDeviceOpticalHeadTypeNumber(BandwidthMode[1], BandwidthModeList))

    return hdl  # Return the device handle


class TunableFilter:
    """
    Class to control the KURIOS Tunable Filter device.

    This class provides methods to open the connection to the device, set the bandwidth and wavelength, and close the connection.
    """

    def __init__(self):
        """
        Initializes the TunableFilter class without connecting to the device.
        """
        self.hdl = None  # Device handle is initialized to None

    def open(self):
        """
        Opens the connection to the first detected KURIOS Tunable Filter device.
        """
        # List connected devices
        devs = KuriosListDevices()
        print(devs)
        if len(devs) <= 0:
            print('There are no devices connected')
            exit()

        # Open the first device
        Kurios = devs[0]
        self.hdl = CommonFunc(Kurios[0])

    def close(self):
        """
        Closes the connection to the KURIOS Tunable Filter device.
        """
        result = KuriosClose(self.hdl)  # Close the device
        if result == 0:
            print("Kurios Close successfully!")
        else:
            print("Kurios Close fail", result)

    def set_bandwidth(self, bandwidth=2):
        """
        Sets the bandwidth mode for the KURIOS Tunable Filter.

        Args:
            bandwidth (int): The bandwidth mode (1 = BLACK; 2 = WIDE; 4 = MEDIUM; 8 = NARROW).

        """
        result = KuriosSetBandwidthMode(self.hdl, bandwidth)
        if result < 0:
            print("Set Bandwidth mode fail", result)
        else:
            print("Set Bandwidth mode :", "WIDE")

        # Verify the current bandwidth mode
        BandwidthMode = [0]
        BandwidthModeList = {1: 'BLACK', 2: 'WIDE', 4: 'MEDIUM', 8: 'NARROW'}
        result = KuriosGetBandwidthMode(self.hdl, BandwidthMode)
        if result < 0:
            print("Get Bandwidth mode fail", result)
        else:
            print("Get Bandwidth mode:", BandwidthModeList.get(BandwidthMode[0]))

    def set_wavelength(self, wavelength=550):
        """
        Sets the wavelength for the KURIOS Tunable Filter.

        Args:
            wavelength (int): The desired wavelength in nanometers (range: 420-730nm).

        """
        result = KuriosSetWavelength(self.hdl, wavelength)
        if result < 0:
            print(f"Set wavelength {wavelength}nm fail", result)


if __name__ == '__main__':
    """
    Main function to test the TunableFilter class.

    Opens the KURIOS Tunable Filter, sets the bandwidth mode, and sweeps through various wavelengths.
    """
    tf = TunableFilter()
    tf.open()

    # Set the bandwidth mode to 'NARROW'
    tf.set_bandwidth(8)

    # Sweep through a range of wavelengths
    for wl in [420, 450, 470, 490, 510, 530, 550, 570, 590, 610, 630, 650, 670, 690, 710]:
        tf.set_wavelength(wl)
        time.sleep(2)

    # Close the connection to the device
    tf.close()
