import re
import time

from KURIOS_COMMAND_LIB import *
def GetDeviceSNCN(IDStr):
    import re
    SNpartern = re.compile('SN(\d{1,10})')
    SNum = re.findall(SNpartern, IDStr)
    CNpartern = re.compile('CN(\d{1,10})')
    CNum = re.findall(CNpartern, IDStr)
    return SNum[0], CNum[0]


def GetDeviceOpticalHeadTypeNumber(hex_string, targe_dict, max_length=4):
    try:
        bin_str = bin(ord(hex_string))

    except Exception as e:
        raise Exception('transert hex {0} to bin error! {1}'.format(hex_string, e))

    parrten = re.compile('0b(\d*)')
    bin_val = parrten.findall(bin_str)[0]
    bin_val_reverse = bin_val[::-1]

    target_ls = []
    for t in range(len(bin_val_reverse)):
        if t < max_length and t in targe_dict.keys():
            if bin_val_reverse[t] == '1':
                target_ls.append(targe_dict[t])
    return target_ls


def CommonFunc(serialNumber):
    hdl = KuriosOpen(serialNumber, 115200, 3)
    # or check by "KuriosIsOpen(devs[0])"
    if (hdl < 0):
        print("Connect ", serialNumber, "fail")
        return -1;
    else:
        print("Connect ", serialNumber, "successful")

    result = KuriosIsOpen(serialNumber)
    print("KuriosIsOpen ", result)

    id = []
    result = KuriosGetId(hdl, id)
    if (result < 0):
        print("KuriosGetId fail ", result)
    else:
        print(id)
        IDString = id
        for s in IDString:
            SN, CN = GetDeviceSNCN(s)
            print("SN: ", SN, "CN: ", CN)
        if (int(SN) >= 212254) and (int(SN) != int(CN)):
            print(
                "KURIOS optical head SN# and controller CN# do not match. It is recommended to use matched optical head and controller for optimum factory calibrated performance.")

    DeviceStatus = [0]
    DeviceStatusList = {0: 'initialization', 1: 'warm up', 2: 'ready'}
    result = KuriosGetStatus(hdl, DeviceStatus)
    if (result < 0):
        print("Get device status fail", result)
    else:
        print("Get device status:", DeviceStatusList.get(DeviceStatus[0]))

    DeviceTem = [0]
    result = KuriosGetTemperature(hdl, DeviceTem)
    if (result < 0):
        print("Get device Temperature fail", result)
    else:
        print("Get device Temperature:", DeviceTem)

    MaxWavelength = [0]
    MinWavelength = [0]
    result = KuriosGetSpecification(hdl, MaxWavelength, MinWavelength)
    if (result < 0):
        print("KuriosGetSpecification fail ", result)
    else:
        print("MaxWavelength: ", MaxWavelength, "MinWavelength: ", MinWavelength)

    SpectrumRange = [0]
    SpectrumRangeList = {0: 'Visible', 1: 'NIR'}
    BandwidthMode = [0]
    BandwidthModeList = {0: 'BLACK', 1: 'WIDE', 2: 'MEDIUM', 3: 'NARROW'}
    result = KuriosGetOpticalHeadType(hdl, SpectrumRange, BandwidthMode)
    if (result < 0):
        print("KuriosGetOpticalHeadType fail ", result)
    else:
        print("filterSpectrumRange: ", GetDeviceOpticalHeadTypeNumber(SpectrumRange[1], SpectrumRangeList),
              "availableBandwidthMode: ", GetDeviceOpticalHeadTypeNumber(BandwidthMode[1], BandwidthModeList))

    return hdl


class TunableFilter:
    def __init__(self):
        self.hdl=None


    def open(self):

        devs = KuriosListDevices()
        print(devs)
        if (len(devs) <= 0):
            print('There is no devices connected')
            exit()

        Kurios = devs[0]

        self.hdl = CommonFunc(Kurios[0])

    def close(self):
        result = KuriosClose(self.hdl)
        if (result == 0):
            print("Kurios Close successfully!")
        else:
            print("Kurios Close fail", result)

    def set_bandwidth(self,bandwidth=2):
        result = KuriosSetBandwidthMode(self.hdl, bandwidth)  # 1 = BLACK; 2 = WIDE; 4 = MEDIUM; 8 = NARROW
        if (result < 0):
            print("Set Bandwidth mode fail", result)
        else:
            print("Set Bandwidth mode :", "WIDE")

        BandwidthMode = [0]
        BandwidthModeList = {1: 'BLACK', 2: 'WIDE', 4: 'MEDIUM', 8: 'NARROW'}
        result = KuriosGetBandwidthMode(self.hdl, BandwidthMode)
        if (result < 0):
            print("Get Bandwidth mode fail", result)
        else:
            print("Get Bandwidth mode:", BandwidthModeList.get(BandwidthMode[0]))

    def set_wavelength(self,wavelength=550):
        result = KuriosSetWavelength(self.hdl,wavelength)
        # the range of wavelength is between MinWavelength and MaxWavelength got in the KuriosGetSpecification function
        # 420-730nm


if __name__ == '__main__':
    tf = TunableFilter()
    tf.open()
    tf.set_bandwidth(8)
    for wl in [420,450,470,490,510,530,550,570,590,610,630,650,670,690,710]:
        tf.set_wavelength(wl)
        time.sleep(2)
    tf.close()
