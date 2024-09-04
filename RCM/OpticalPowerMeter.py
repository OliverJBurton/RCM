import pyvisa as visa
from pyvisa.constants import Parity, StopBits
import time

class PM16_120:
  def __init__(self):
    self.rm = visa.ResourceManager()
    try:
      self.inst = self.rm.open_resource("USB0::0x1313::0x807B::230620213::INSTR")
      try:
        print(f"Power meter is online: {self.inst.query('*IDN?')}")
      except TimeoutError:
        print("Power meter failed to initialise")
    except:
      print("Power meter not found. Did you plug it in?")

  def get_power_reading_W(self):
    return self.inst.query("Read?")

  def set_wavelength(self, wavelength):
    if not 400 <= wavelength <= 1100:
      raise ValueError("{} nm is not in [400, 1100] nm range".format(wavelength))

    self.inst.write("SENS:CORR:WAV {}".format(wavelength))

  def get_wavelength_setting(self):
    wavelength = float(self.inst.query("SENS:CORR:WAV?"))
    print(f"Wavelength is set to {wavelength} nm")
    return wavelength

if __name__ == "__main__":
  light_reader = PM16_120()
  light_reader.set_wavelength(405)
  light_reader.get_wavelength_setting()
  print(light_reader.get_power_reading_W())
  # print(light_reader.read())


