import pyvisa as visa
from pyThorlabsPM100x.driver import ThorlabsPM100x
from ThorlabsPM100 import ThorlabsPM100

#Need to download ThorlabsPM100 module: pip3 install ThorlabsPM100

class PM100:
  def __init__(self):
    rm = visa.ResourceManager()
    print(rm.list_resources())
    inst = rm.open_resource('ASRL5::INSTR', timeout=1)
    self.power_meter = ThorlabsPM100(inst=inst)

  def read(self):
    return self.power_meter.read


if __name__ == "__main__":
  light_reader = PM100()
  print(light_reader.read())



