import pyvisa

#Need to download ThorlabsPM100 module: pip3 install ThorlabsPM100

class PM100:
  def __init__(self):
    
    inst = visa.instrument('USB0::0x0000::0x0000::DG5Axxxxxxxxx::INSTR', term_chars='\n', timeout=1)
    self.power_meter = ThorlabsPM100(inst = inst)

  def read(self):
    return self.power_meter.read


  