# Import the PyVISA library, which provides control of measurement devices, and the time library.
import pyvisa
import time

class DC2200:
    """
    A class to control the Thorlabs DC2200 LED controller using PyVISA.
    This class allows for communication with the device, setting brightness levels, and switching the LED on or off.
    """

    def __init__(self):
        """
        Initializes the DC2200 class, connects to the device, and prints its identification information.

        The connection is made via PyVISA's resource manager. You must ensure that the correct USB serial number is provided for your device.
        """
        # Opens a resource manager to manage connections to instruments.
        self.rm = pyvisa.ResourceManager()

        # Opens the connection to the device using its unique USB identifier.
        # Note: Replace the serial number in the USB string with your device's serial number.
        self.instr = self.rm.open_resource('USB0::0x1313::0x80C8::M00960538::INSTR')

        # Queries and prints the identification information for the connected device.
        # The *IDN? command returns the device identification.
        print("Used device:", self.instr.query("*IDN?"))

    def set_brightness(self, percent=1.1):
        """
        Sets the brightness of the LED in constant current mode.

        Args:
            percent (float): The brightness percentage to set (default is 1.1%).

        The brightness value is passed as a string command to the device, and the LED is set to constant current mode.
        """
        # Set the LED controller to constant current mode (CB = Constant Brightness).
        self.instr.write("SOURCE1:MODE CB")

        # Create the command string for setting the brightness percentage.
        command = "SOURCE1:CBRIGHTNESS:BRIGHTNESS " + str(percent)

        # Write the command to the device to set the brightness.
        self.instr.write(command)

        # Print confirmation of the brightness level.
        print('Set brightness to ' + str(percent) + '%')

    def on(self):
        """
        Switches the LED on by sending the appropriate command to the DC2200 controller.
        """
        # Command to turn the LED output on.
        self.instr.write("OUTPUT1:STATE ON")
        print("Switch LED on.")

    def off(self):
        """
        Switches the LED off by sending the appropriate command to the DC2200 controller.
        """
        # Command to turn the LED output off.
        self.instr.write("OUTPUT1:STATE OFF")
        print("Switch LED off.")

    def close(self):
        """
        Closes the connection to the DC2200 device and the resource manager.

        This method should be called when communication with the device is complete to release resources.
        """
        # Closes the connection to the instrument.
        self.instr.close()

        # Closes the resource manager.
        self.rm.close()
        print("Connection closed.")

if __name__ == '__main__':
    """
    Example of using the DC2200 class to control the LED.

    Connects to the DC2200, sets the brightness to various levels, and switches the LED on and off.
    """
    # Print message indicating connection is starting.
    print('Connecting to the DC2200 LED controller...')

    # Create an instance of the DC2200 class to communicate with the device.
    light = DC2200()

    # Set brightness levels and toggle the LED on/off with delays in between.
    light.set_brightness(0.5)  # Set brightness to 0.5%
    light.on()                  # Turn the LED on
    time.sleep(1)               # Wait for 1 second

    light.set_brightness(1.5)   # Set brightness to 1.5%
    time.sleep(1)               # Wait for 1 second

    light.set_brightness(2.0)   # Set brightness to 2.0%
    time.sleep(1)               # Wait for 1 second

    light.set_brightness(1.9)   # Set brightness to 1.9%
    time.sleep(1)               # Wait for 1 second

    # Turn the LED off after adjusting brightness.
    light.off()

    # Close the connection to the device.
    light.close()
