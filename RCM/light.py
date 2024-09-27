#Import the PyVISA and time library to Python.
import pyvisa
import time


class DC2200:
    def __init__(self):
        # see https://github.com/Thorlabs/Current_And_Temperature_Controller_Examples/blob/main/Python/DC2200%20LED%20Controllers/DC2200%20with%20PyVISA.py

        #Opens a resource manager
        self.rm = pyvisa.ResourceManager()

        #Opens the connection to the device. The variable instr is the handle for the device.
        # !!! In the USB number the serial number (M00...) needs to be changed to the one of the connected device.
        self.instr = self.rm.open_resource('USB0::0x1313::0x80C8::M00960538::INSTR')

        #The command instr.query can be used when you want to get data from the device.
        # *IDN? returns the identification of the device.
        print("Used device:", self.instr.query("*IDN?"))

    def set_brightness(self, percent=1.1):
        # The command instr.write can be used to write data to the device when you do not expect a response from the device.
        # Set the DC2200 to brightness mode, set the brightness level, switch the LED on.
        # see DC2200 documentation
        self.instr.write("SOURCE1:MODE CB")
        command = "SOURCE1:CBRIGHTNESS:BRIGHTNESS " + str(percent)
        self.instr.write(command)
        print('Set brightness to ' + str(percent) + '%')
    
    def set_current_mA(self, current_mA):
        # Set the DC2200 to constant current mode, set the current level, switch the LED on.
        if current_mA < 0:
            raise ValueError("Current must be positive!")
        elif current_mA > 1000:
            print("Maximum of 1000 mA exceeded, setting value to 1000 mA")
            current_mA = 1000

        self.instr.write("SOURCE1:MODE 1")
        self.instr.write(f"SOURCE1:CCURENT:CURRENT {current_mA/1000}")
        print(f"Set current to {current_mA} mA")
    
    def on(self):
        '''
        Switches LED on
        :return:
        '''
        self.instr.write("OUTPUT1:STATE ON")
        print("Switch LED on.")

    def off(self):
        '''
        switches LED off
        :return:
        '''
        self.instr.write("OUTPUT1:STATE OFF")

    def close(self):
        '''
        closes connection
        :return:
        '''
        self.instr.close()
        self.rm.close()


if __name__ == '__main__':
    print('connecting')
    light = DC2200()
    light.set_current_mA(500)
    light.on()
    # time.sleep(5)
    light.off()
    # light.close()
