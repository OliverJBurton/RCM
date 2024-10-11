# Importing the ctypes library to work with C data types and to interact with dynamic link libraries (DLLs) in Python.
from ctypes import *

#region import dll functions

# Loading the Thorlabs Kurios SDK library (DLL) using ctypes.cdll to access its functions.
KuriosLib = cdll.LoadLibrary(r"C:\Program Files (x86)\Thorlabs\Kurios\Sample\Thorlabs_Kurios_C++SDK\KURIOS_COMMAND_LIB_Win64.dll")

# Define function prototypes for the commands available in the Kurios SDK.

# Opens a Kurios device by its serial number.
cmdOpen = KuriosLib.common_Open
cmdOpen.restype = c_int  # Return type is an integer.
cmdOpen.argtypes = [c_char_p, c_int, c_int]  # Arguments are a string (device serial), baud rate, and timeout.

# Checks if a Kurios device is open by its serial number.
cmdIsOpen = KuriosLib.common_IsOpen
cmdOpen.restype = c_int  # Return type is an integer.
cmdOpen.argtypes = [c_char_p]  # Argument is the serial number of the device (string).

# Lists all connected Kurios devices.
cmdList = KuriosLib.common_List
cmdList.argtypes = [c_char_p]  # Argument is a buffer to store the list.
cmdList.restype = c_int  # Return type is an integer.

# Retrieves the device ID for a Kurios device.
cmdGetId = KuriosLib.kurios_Get_ID
cmdGetId.restype = c_int  # Return type is an integer.
cmdGetId.argtypes = [c_int, c_char_p]  # Arguments are the device handle (integer) and a buffer to store the ID.

# Retrieves the specifications (wavelength range) of a connected Kurios filter.
cmdGetSpecification = KuriosLib.kurios_Get_Specification
cmdGetSpecification.restype = c_int  # Return type is an integer.
cmdGetSpecification.argtypes = [c_int, POINTER(c_int), POINTER(c_int)]  # Arguments: device handle, max wavelength, min wavelength.

# Retrieves the type of optical head for a connected Kurios filter.
cmdGetOpticalHeadType = KuriosLib.kurios_Get_OpticalHeadType
cmdGetOpticalHeadType.restype = c_int  # Return type is an integer.
cmdGetOpticalHeadType.argtypes = [c_int, c_char_p, c_char_p]  # Arguments: device handle, spectrum range, bandwidth mode.

# Retrieves the current output mode of the Kurios device.
cmdGetOutputMode = KuriosLib.kurios_Get_OutputMode
cmdGetOutputMode.restype = c_int  # Return type is an integer.
cmdGetOutputMode.argtypes = [c_int, POINTER(c_int)]  # Arguments: device handle, output mode.

# Sets the output mode of the Kurios device.
cmdSetOutputMode = KuriosLib.kurios_Set_OutputMode
cmdSetOutputMode.restype = c_int  # Return type is an integer.
cmdSetOutputMode.argtypes = [c_int, c_int]  # Arguments: device handle, output mode value.

# Retrieves the current bandwidth mode of the Kurios filter.
cmdGetBandwidthMode = KuriosLib.kurios_Get_BandwidthMode
cmdGetBandwidthMode.restype = c_int  # Return type is an integer.
cmdGetBandwidthMode.argtypes = [c_int, POINTER(c_int)]  # Arguments: device handle, bandwidth mode.

# Sets the bandwidth mode of the Kurios filter.
cmdSetBandwidthMode = KuriosLib.kurios_Set_BandwidthMode
cmdSetBandwidthMode.restype = c_int  # Return type is an integer.
cmdSetBandwidthMode.argtypes = [c_int, c_int]  # Arguments: device handle, bandwidth mode value.

# Retrieves the current wavelength of the Kurios filter.
cmdGetWavelength = KuriosLib.kurios_Get_Wavelength
cmdGetWavelength.restype = c_int  # Return type is an integer.
cmdGetWavelength.argtypes = [c_int, POINTER(c_int)]  # Arguments: device handle, wavelength.

# Sets the wavelength of the Kurios filter.
cmdSetWavelength = KuriosLib.kurios_Set_Wavelength
cmdSetWavelength.restype = c_int  # Return type is an integer.
cmdSetWavelength.argtypes = [c_int, c_int]  # Arguments: device handle, wavelength.

# Retrieves sequence step data from the Kurios filter.
cmdGetSequenceStepData = KuriosLib.kurios_Get_SequenceStepData
cmdGetSequenceStepData.restype = c_int  # Return type is an integer.
cmdGetSequenceStepData.argtypes = [c_int, c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int)]  # Arguments: device handle, step index, wavelength, interval, bandwidth mode.

# Sets sequence step data for the Kurios filter.
cmdSetSequenceStepData = KuriosLib.kurios_Set_SequenceStepData
cmdSetSequenceStepData.restype = c_int  # Return type is an integer.
cmdSetSequenceStepData.argtypes = [c_int, c_int, c_int, c_int, c_int]  # Arguments: device handle, step index, wavelength, interval, bandwidth mode.

# Retrieves all sequence data from the Kurios filter.
cmdGetAllSequenceData = KuriosLib.kurios_Get_AllSequenceData
cmdGetAllSequenceData.restype = c_int  # Return type is an integer.
cmdGetAllSequenceData.argtypes = [c_int, c_char_p]  # Arguments: device handle, buffer for sequence data.

# Inserts a sequence step in the Kurios filter.
cmdSetInsertSequenceStep = KuriosLib.kurios_Set_InsertSequenceStep
cmdSetInsertSequenceStep.restype = c_int  # Return type is an integer.
cmdSetInsertSequenceStep.argtypes = [c_int, c_int, c_int, c_int, c_int]  # Arguments: device handle, step index, wavelength, interval, bandwidth mode.

# Deletes a sequence step from the Kurios filter.
cmdSetDeleteSequenceStep = KuriosLib.kurios_Set_DeleteSequenceStep
cmdSetDeleteSequenceStep.restype = c_int  # Return type is an integer.
cmdSetDeleteSequenceStep.argtypes = [c_int, c_int]  # Arguments: device handle, step index.

# Sets the default wavelength for a sequence in the Kurios filter.
cmdSetDefaultWavelengthForSequence = KuriosLib.kurios_Set_DefaultWavelengthForSequence
cmdSetDefaultWavelengthForSequence.restype = c_int  # Return type is an integer.
cmdSetDefaultWavelengthForSequence.argtypes = [c_int, c_int]  # Arguments: device handle, wavelength.

# Retrieves the default wavelength for a sequence in the Kurios filter.
cmdGetDefaultWavelengthForSequence = KuriosLib.kurios_Get_DefaultWavelengthForSequence
cmdGetDefaultWavelengthForSequence.restype = c_int  # Return type is an integer.
cmdGetDefaultWavelengthForSequence.argtypes = [c_int, POINTER(c_int)]  # Arguments: device handle, default wavelength.

# Sets the default bandwidth mode for a sequence in the Kurios filter.
cmdSetDefaultBandwidthForSequence = KuriosLib.kurios_Set_DefaultBandwidthForSequence
cmdSetDefaultBandwidthForSequence.restype = c_int  # Return type is an integer.
cmdSetDefaultBandwidthForSequence.argtypes = [c_int, c_int]  # Arguments: device handle, bandwidth mode.

# Retrieves the default bandwidth mode for a sequence in the Kurios filter.
cmdGetDefaultBandwidthForSequence = KuriosLib.kurios_Get_DefaultBandwidthForSequence
cmdGetDefaultBandwidthForSequence.restype = c_int  # Return type is an integer.
cmdGetDefaultBandwidthForSequence.argtypes = [c_int, POINTER(c_int)]  # Arguments: device handle, default bandwidth mode.

# Sets the default time interval for a sequence in the Kurios filter.
cmdSetDefaultTimeIntervalForSequence = KuriosLib.kurios_Set_DefaultTimeIntervalForSequence
cmdSetDefaultTimeIntervalForSequence.restype = c_int  # Return type is an integer.
cmdSetDefaultTimeIntervalForSequence.argtypes = [c_int, c_int]  # Arguments: device handle, time interval.

# Retrieves the default time interval for a sequence in the Kurios filter.
cmdGetDefaultTimeIntervalForSequence = KuriosLib.kurios_Get_DefaultTimeIntervalForSequence
cmdGetDefaultTimeIntervalForSequence.restype = c_int  # Return type is an integer.
cmdGetDefaultTimeIntervalForSequence.argtypes = [c_int, POINTER(c_int)]  # Arguments: device handle, default time interval.

# Retrieves the sequence length for the Kurios filter.
cmdGetSequenceLength = KuriosLib.kurios_Get_SequenceLength
cmdGetSequenceLength.restype = c_int  # Return type is an integer.
cmdGetSequenceLength.argtypes = [c_int, POINTER(c_int)]  # Arguments: device handle, sequence length.

# Retrieves the current status of the Kurios filter.
cmdGetStatus = KuriosLib.kurios_Get_Status
cmdGetStatus.restype = c_int  # Return type is an integer.
cmdGetStatus.argtypes = [c_int, POINTER(c_int)]  # Arguments: device handle, status.

# Retrieves the current temperature of the Kurios filter.
cmdGetTemperature = KuriosLib.kurios_Get_Temperature
cmdGetTemperature.restype = c_int  # Return type is an integer.
cmdGetTemperature.argtypes = [c_int, POINTER(c_double)]  # Arguments: device handle, temperature.

# Sets the trigger out signal mode for the Kurios filter.
cmdSetTriggerOutSignalMode = KuriosLib.kurios_Set_TriggerOutSignalMode
cmdSetTriggerOutSignalMode.restype = c_int  # Return type is an integer.
cmdSetTriggerOutSignalMode.argtypes = [c_int, c_int]  # Arguments: device handle, trigger out mode.

# Retrieves the trigger out signal mode for the Kurios filter.
cmdGetTriggerOutSignalMode = KuriosLib.kurios_Get_TriggerOutSignalMode
cmdGetTriggerOutSignalMode.restype = c_int  # Return type is an integer.
cmdGetTriggerOutSignalMode.argtypes = [c_int, POINTER(c_int)]  # Arguments: device handle, trigger out mode.

# Forces a trigger in external triggered sequence mode for the Kurios filter.
cmdSetForceTrigger = KuriosLib.kurios_Set_ForceTrigger
cmdSetForceTrigger.restype = c_int  # Return type is an integer.
cmdSetForceTrigger.argtypes = [c_int]  # Argument: device handle.

#endregion

#region command for Kurios

def KuriosListDevices():
    """
    List all connected Kurios devices.

    Returns:
        List of Kurios devices, where each item is a pair [serialNumber, descriptor].
    """
    str = create_string_buffer(1024, '\0')
    result = cmdList(str)
    devicesStr = str.raw.decode("utf-8").rstrip('\x00').split(',')
    length = len(devicesStr)
    i = 0
    devices = []
    devInfo = ["", ""]
    while(i < length):
        str = devicesStr[i]
        if (i % 2 == 0):
            if str != '':
                devInfo[0] = str
            else:
                i += 1
        else:
            isFind = False
            if(str.find("KURIOS") >= 0):
                isFind = True
            if isFind:
                devInfo[1] = str
                devices.append(devInfo.copy())
        i += 1
    return devices

def KuriosOpen(serialNo, nBaud, timeout):
    """
    Open a Kurios device.

    Args:
        serialNo (str): Serial number of the device to be opened.
        nBaud (int): Bit rate of the port (baud rate).
        timeout (int): Timeout value in seconds.

    Returns:
        int: Non-negative value indicates success (handle number); negative value indicates failure.
    """
    return cmdOpen(serialNo.encode('utf-8'), nBaud, timeout)

def KuriosIsOpen(serialNo):
    """
    Check if a Kurios device is open.

    Args:
        serialNo (str): Serial number of the device to check.

    Returns:
        int: 1 if the device is open; 0 if the device is not open.
    """
    return cmdIsOpen(serialNo.encode('utf-8'))

def KuriosClose(hdl):
    """
    Close an open Kurios device.

    Args:
        hdl (int): The handle of the opened device.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    return KuriosLib.common_Close(hdl)

def KuriosGetId(hdl, id):
    """
    Get the product header and firmware version of the Kurios device.

    Args:
        hdl (int): The handle of the opened device.
        id (list): List to store the device ID.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    idStr = create_string_buffer(1024, '\0')
    ret = cmdGetId(hdl, idStr)
    id.append(idStr.raw.decode("utf-8").rstrip('\x00'))
    return ret

def KuriosGetSpecification(hdl, Max, Min):
    """
    Get the wavelength range of the connected Kurios filter.

    Args:
        hdl (int): The handle of the opened device.
        Max (list): List to store the maximum wavelength.
        Min (list): List to store the minimum wavelength.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    Maximum = c_int(0)
    Minimum = c_int(0)
    ret = cmdGetSpecification(hdl, Maximum, Minimum)
    Max[0] = Maximum.value
    Min[0] = Minimum.value
    return ret

def KuriosGetOpticalHeadType(hdl, filterSpectrumRange, availableBandwidthMode):
    """
    Get the filter's spectrum range and available bandwidth modes.

    Args:
        hdl (int): The handle of the opened device.
        filterSpectrumRange (list): List to store the filter spectrum range.
        availableBandwidthMode (list): List to store the available bandwidth modes.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    SpectrumRange = create_string_buffer(1024, '\0')
    BandwidthMode = create_string_buffer(1024, '\0')
    ret = cmdGetOpticalHeadType(hdl, SpectrumRange, BandwidthMode)
    filterSpectrumRange.append(SpectrumRange.raw.decode("utf-8").rstrip('\x00'))
    availableBandwidthMode.append(BandwidthMode.raw.decode("utf-8").rstrip('\x00'))
    return ret

def KuriosSetOutputMode(hdl, value):
    """
    Set the output mode of the Kurios device.

    Args:
        hdl (int): The handle of the opened device.
        value (int): Output mode (1 = manual, 2 = sequenced, 3 = external trigger, etc.).

    Returns:
        int: 0 if successful; negative value if failed.
    """
    return cmdSetOutputMode(hdl, value)

def KuriosGetOutputMode(hdl, value):
    """
    Get the current output mode of the Kurios device.

    Args:
        hdl (int): The handle of the opened device.
        value (list): List to store the current output mode.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    val = c_int(0)
    ret = cmdGetOutputMode(hdl, val)
    value[0] = val.value
    return ret

def KuriosSetBandwidthMode(hdl, value):
    """
    Set the bandwidth mode of the Kurios device.

    Args:
        hdl (int): The handle of the opened device.
        value (int): Bandwidth mode (1 = BLACK, 2 = WIDE, 4 = MEDIUM, etc.).

    Returns:
        int: 0 if successful; negative value if failed.
    """
    return cmdSetBandwidthMode(hdl, value)

def KuriosGetBandwidthMode(hdl, value):
    """
    Get the current bandwidth mode of the Kurios device.

    Args:
        hdl (int): The handle of the opened device.
        value (list): List to store the current bandwidth mode.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    val = c_int(0)
    ret = cmdGetBandwidthMode(hdl, val)
    value[0] = val.value
    return ret

def KuriosSetWavelength(hdl, value):
    """
    Set the wavelength of the Kurios filter.

    Args:
        hdl (int): The handle of the opened device.
        value (int): The wavelength to set (within the available range).

    Returns:
        int: 0 if successful; negative value if failed.
    """
    return cmdSetWavelength(hdl, value)

def KuriosGetWavelength(hdl, value):
    """
    Get the current wavelength of the Kurios filter.

    Args:
        hdl (int): The handle of the opened device.
        value (list): List to store the current wavelength.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    val = c_int(0)
    ret = cmdGetWavelength(hdl, val)
    value[0] = val.value
    return ret

def KuriosSetSequenceStepData(hdl, Index, wavelength, interval, bandwidthMode):
    """
    Set sequence step data for the Kurios filter.

    Args:
        hdl (int): The handle of the opened device.
        Index (int): Step index.
        wavelength (int): Wavelength within the filter range.
        interval (int): Time interval for the step.
        bandwidthMode (int): Bandwidth mode for the step.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    return cmdSetSequenceStepData(hdl, Index, wavelength, interval, bandwidthMode)

def KuriosGetSequenceStepData(hdl, Index, wavelength, interval, bandwidthMode):
    """
    Get sequence step data for the Kurios filter.

    Args:
        hdl (int): The handle of the opened device.
        Index (int): Step index.
        wavelength (list): List to store the wavelength for the step.
        interval (list): List to store the time interval for the step.
        bandwidthMode (list): List to store the bandwidth mode for the step.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    Ind = c_int(0)
    wavele = c_int(0)
    inter = c_int(0)
    bandM = c_int(0)
    ret = cmdGetSequenceStepData(hdl, Ind, wavele, inter, bandM)
    wavelength[0] = wavele.value
    interval[0] = inter.value
    bandwidthMode[0] = bandM.value
    return ret

def KuriosGetAllSequenceData(hdl, value):
    """
    Get all sequence data (wavelength and time intervals) for the Kurios filter.

    Args:
        hdl (int): The handle of the opened device.
        value (list): List to store the sequence data.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    val = create_string_buffer(1024, '\0')
    ret = cmdGetAllSequenceData(hdl, val)
    value.append(val.raw.decode("utf-8").rstrip('\x00'))
    return ret

def KuriosSetInsertSequenceStep(hdl, index, wavelength, interval, bandwidthMode):
    """
    Insert a sequence step in the Kurios filter.

    Args:
        hdl (int): The handle of the opened device.
        index (int): Index for the sequence step.
        wavelength (int): Wavelength for the step.
        interval (int): Time interval for the step.
        bandwidthMode (int): Bandwidth mode for the step.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    return cmdSetInsertSequenceStep(hdl, index, wavelength, interval, bandwidthMode)

def KuriosSetDeleteSequenceStep(hdl, value):
    """
    Delete a sequence step from the Kurios filter.

    Args:
        hdl (int): The handle of the opened device.
        value (int): Index of the step to delete (0 to delete all steps).

    Returns:
        int: 0 if successful; negative value if failed.
    """
    return cmdSetDeleteSequenceStep(hdl, value)

def KuriosSetDefaultWavelengthForSequence(hdl, value):
    """
    Set the default wavelength for all steps in the sequence.

    Args:
        hdl (int): The handle of the opened device.
        value (int): Default wavelength for the sequence.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    return cmdSetDefaultWavelengthForSequence(hdl, value)

def KuriosGetDefaultWavelengthForSequence(hdl, value):
    """
    Get the default wavelength for all steps in the sequence.

    Args:
        hdl (int): The handle of the opened device.
        value (list): List to store the default wavelength.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    val = c_int(0)
    ret = cmdGetDefaultWavelengthForSequence(hdl, val)
    value[0] = val.value
    return ret

def KuriosSetDefaultBandwidthForSequence(hdl, value):
    """
    Set the default bandwidth mode for all steps in the sequence.

    Args:
        hdl (int): The handle of the opened device.
        value (int): Default bandwidth mode for the sequence (e.g., 2 for WIDE, 4 for MEDIUM).

    Returns:
        int: 0 if successful; negative value if failed.
    """
    return cmdSetDefaultBandwidthForSequence(hdl, value)

def KuriosGetDefaultBandwidthForSequence(hdl, value):
    """
    Get the default bandwidth mode for all steps in the sequence.

    Args:
        hdl (int): The handle of the opened device.
        value (list): List to store the default bandwidth mode.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    val = c_int(0)
    ret = cmdGetDefaultBandwidthForSequence(hdl, val)
    value[0] = val.value
    return ret

def KuriosSetDefaultTimeIntervalForSequence(hdl, value):
    """
    Set the default time interval for all steps in the sequence.

    Args:
        hdl (int): The handle of the opened device.
        value (int): Default time interval for the sequence (in milliseconds).

    Returns:
        int: 0 if successful; negative value if failed.
    """
    return cmdSetDefaultTimeIntervalForSequence(hdl, value)

def KuriosGetDefaultTimeIntervalForSequence(hdl, value):
    """
    Get the default time interval for all steps in the sequence.

    Args:
        hdl (int): The handle of the opened device.
        value (list): List to store the default time interval (in milliseconds).

    Returns:
        int: 0 if successful; negative value if failed.
    """
    val = c_int(0)
    ret = cmdGetDefaultTimeIntervalForSequence(hdl, val)
    value[0] = val.value
    return ret

def KuriosGetSequenceLength(hdl, value):
    """
    Get the length of the current sequence.

    Args:
        hdl (int): The handle of the opened device.
        value (list): List to store the sequence length.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    val = c_int(0)
    ret = cmdGetSequenceLength(hdl, val)
    value[0] = val.value
    return ret

def KuriosGetStatus(hdl, value):
    """
    Get the current status of the Kurios filter.

    Args:
        hdl (int): The handle of the opened device.
        value (list): List to store the current status (0 = initialization, 1 = warm up, 2 = ready).

    Returns:
        int: 0 if successful; negative value if failed.
    """
    val = c_int(0)
    ret = cmdGetStatus(hdl, val)
    value[0] = val.value
    return ret

def KuriosGetTemperature(hdl, value):
    """
    Get the current temperature of the Kurios filter.

    Args:
        hdl (int): The handle of the opened device.
        value (list): List to store the current temperature.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    val = c_double(0)
    ret = cmdGetTemperature(hdl, val)
    value[0] = val.value
    return ret

def KuriosSetTriggerOutSignalMode(hdl, value):
    """
    Set the trigger out signal mode of the Kurios filter.

    Args:
        hdl (int): The handle of the opened device.
        value (int): Trigger out mode (0 = normal, 1 = flipped).

    Returns:
        int: 0 if successful; negative value if failed.
    """
    return cmdSetTriggerOutSignalMode(hdl, value)

def KuriosGetTriggerOutSignalMode(hdl, value):
    """
    Get the trigger out signal mode of the Kurios filter.

    Args:
        hdl (int): The handle of the opened device.
        value (list): List to store the current trigger out mode (0 = normal, 1 = flipped).

    Returns:
        int: 0 if successful; negative value if failed.
    """
    val = c_int(0)
    ret = cmdGetTriggerOutSignalMode(hdl, val)
    value[0] = val.value
    return ret

def KuriosSetForceTrigger(hdl):
    """
    Force a trigger in the external triggered sequence mode (requires Firmware version 3.1 or above).

    Args:
        hdl (int): The handle of the opened device.

    Returns:
        int: 0 if successful; negative value if failed.
    """
    return cmdSetForceTrigger(hdl)

#endregion
