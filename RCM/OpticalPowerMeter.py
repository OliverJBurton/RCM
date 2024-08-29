import pyvisa as visa
from ThorlabsPM100 import ThorlabsPM100
import time

#Need to download ThorlabsPM100 module: pip3 install ThorlabsPM100

class PM100:
  def __init__(self):
    self.power_meter = ThorlabsPM100x()
    print(power_meter.available_devices)
    self.rm = visa.ResourceManager()
    
    inst = self.rm.open_resource('ASRL5::INSTR', 
    baud_rate=9600, 
    data_bits=8,
    parity=Parity.none, 
    write_termination='\n', 
    read_termination="\n", 
    stop_bits=StopBits.one,
    timeout=1000)

    # inst.write('*IDN?')
    # while True:
    #   print(inst.read_bytes(1))

    self.power_meter = ThorlabsPM100(inst = inst, verbose=True)

  def read(self):
    return self.power_meter.read


if __name__ == "__main__":
  light_reader = PM100()
  print(light_reader.read())


