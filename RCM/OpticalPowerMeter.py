import pyvisa as visa
from ThorlabsPM100 import ThorlabsPM100
from pyvisa.constants import Parity, StopBits
import time

#Need to download ThorlabsPM100 module: pip3 install ThorlabsPM100

class PM100:
  def __init__(self):
    self.rm = visa.ResourceManager()
    print(self.rm.list_resources())
    
    inst = self.rm.open_resource('ASRL/dev/cu.usbserial-FT65H2R6::INSTR', 
    baud_rate=9600, 
    data_bits=8,
    parity=Parity.none, 
    write_termination='\x0A',
    read_termination='\x0A', 
    stop_bits=StopBits.one,
    timeout=1000)

    inst.write('*IDN?')
    time.sleep(1)
    print(inst.read_bytes(1))

    # self.power_meter = ThorlabsPM100(inst = inst, verbose=True)

  def read(self):
    return self.power_meter.read


if __name__ == "__main__":
  light_reader = PM100()
  # print(light_reader.read())


