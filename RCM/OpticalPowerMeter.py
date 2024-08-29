import pyvisa as visa
from ThorlabsPM100 import ThorlabsPM100

#Need to download ThorlabsPM100 module: pip3 install ThorlabsPM100

class PM100:
  def __init__(self):
    self.rm = visa.ResourceManager()
    
    inst = self.rm.open_resource('ASRL5::INSTR', timeout=500)

    inst.write('*IDN?')
    while True:
      print(inst.read_bytes(1))

    # self.power_meter = ThorlabsPM100(inst = inst, verbose=True)

  def read(self):
    return self.power_meter.read


if __name__ == "__main__":
  light_reader = PM100()
  print(light_reader.rm.list_resources())
  # print(light_reader.read())


  