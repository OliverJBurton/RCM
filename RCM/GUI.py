import tkinter as tk
from time import sleep
from threading import Thread, Event
from queue import Empty, Queue
#from OpticalPowerMeter import PM100
import sys

class _CallData:
  def __init__(self, fn, args, kwargs):
    self.fn = fn
    self.args = args
    self.kwargs = kwargs

class experimentGUI(tk.Tk):
  def __init__(self, step=5, xNum=20, yNum=20):
    super().__init__()
    self.canvas = tk.Canvas(self, bg="#FFFFFF", highlightthickness=0)
    self.canvas.pack(fill="both", expand=True)

    # Initialise power meter
    #self.power_meter = PM100()

    # Create event queue
    self.request_queue = Queue()

    self.xNum = xNum
    self.yNum = yNum
    

    self.step = step
    # Initialise greyscale_intensity_readings
    self.greyscale_intensity_readings = []
    # Creates a thread for the greyscale intensity experiment
    self.greyscale_intensity_experiment_thread = Thread(target=self.greyscale_intensity_experiment, daemon=True)

    # Checks the event queue every 500 ms
    self.after(500, self.call_handler)

  def activate_full_screen(self):
    self.attributes("-fullscreen", True)

  def set_brightness(self, color):
    self.canvas.config(bg=color)

  def initialise_rectangle(self, width, height):
    self.canvas.create_rectangle(0,0,width,height, fill="#FFFFFF", width=0)
  
  def end_experiment(self):
    self.destroy()

  def call_handler(self):
    try:
      data = self.request_queue.get_nowait()
      data.fn(*data.args, *data.kwargs)
    except Empty:
      pass

    self.after(500, self.call_handler)
  
  def make_call(self, fn, *args, **kwargs):
    data = _CallData(fn, args, kwargs)
    self.request_queue.put(data)
  
  def greyscale_intensity_experiment(self):
    print("Move the screen to the projected screen, type 'done' to continue.")
    while sys.stdin.read(4) != "done":
      print("type 'done' to continue")
    print("Begining experiment")
    self.make_call(self.activate_full_screen)
    
    for i in range(255, 0, -step):
      greyscale = "#" + "{:02x}".format(i)*3
      self.make_call(self.set_brightness, greyscale)
      #self.greyscale_intensity_readings.append([greyscale, self.power_meter.read()])
    self.make_call(self.destroy)
  
  def pixel_intensity_experiment(self):


  


if __name__ == "__main__":
  screen = experimentGUI()
  screen.greyscale_intensity_experiment_thread.start()
  screen.mainloop()