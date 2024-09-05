import pyvisa as visa
from pyvisa.constants import Parity, StopBits
import time

class PM16_120:
  '''
  Enables control of the PM16-120 USB optical power meter
  '''
  def __init__(self):
    self.rm = visa.ResourceManager()
    try:
      # Value inside brackets must be address of the USB port
      # Use print(self.rm.list_resources()) to determine port address
      self.inst = self.rm.open_resource("USB0::0x1313::0x807B::230620213::INSTR")
      try:
        # Prints identification number if device is connected
        print(f"Power meter is online: {self.inst.query('*IDN?')}")
      except TimeoutError:
        print("Power meter failed to initialise")
    except:
      print("Power meter not found. Did you plug it in?")

  def get_power_reading_W(self):
    '''
    Gets light intensity reading from the PM16-120

    :returns: light intensity in watts

    '''
    return self.inst.query("Read?")

  def set_wavelength(self, wavelength_nm):
    '''
    Sets wavelength of the PM16-120

    :param wavelength_nm: wavelength in nanometers

    '''
    # Checks if wavelength is within limit of device
    if not 400 <= wavelength_nm <= 1100:
      raise ValueError("{} nm is not in [400, 1100] nm range".format(wavelength_nm))

    self.inst.write("SENS:CORR:WAV {}".format(wavelength_nm))

  def get_wavelength_setting(self):
    '''
    Prints and returns the wavelength of the PM16-120

    :return wavelength_nm: wavelength in nanometers

    '''
    wavelength_nm = float(self.inst.query("SENS:CORR:WAV?"))
    print(f"Wavelength is set to {wavelength_nm} nm")
    return wavelength_nm

if __name__ == "__main__":
  light_reader = PM16_120()
  light_reader.set_wavelength(405)
  light_reader.get_wavelength_setting()
  print(light_reader.get_power_reading_W())
  # print(light_reader.read())


