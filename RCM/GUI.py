import tkinter as tk
from time import sleep
from threading import Thread, Event
from queue import Empty, Queue
#from OpticalPowerMeter import PM100
import sys
import numpy as np

class _CallData:
  def __init__(self, fn, args, kwargs):
    self.fn = fn
    self.args = args
    self.kwargs = kwargs

class experimentGUI(tk.Tk):
  def __init__(self, step=5, xNum=5, yNum=5):
    super().__init__()
    self.columnconfigure(0, weight=1)
    self.rowconfigure(0, weight=1)
    self.canvas = tk.Canvas(self, bg="#FFFFFF", highlightthickness=0)
    self.canvas.pack(fill="both", expand=True)

    # Initialise power meter
    #self.power_meter = PM100()

    # Create event queue
    self.request_queue = Queue()

    self.xNum = xNum
    self.yNum = yNum
    self.rectangle = None
    self.intensity_readings = [[0 for i in range(self.yNum)] for j in range(self.xNum)]
    self.pixel_intensity_experiment_thread = Thread(target=self.pixel_intensity_experiment, daemon=True)

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
    self.rectangle = self.canvas.create_rectangle(0, 0, width,height, fill="#000000", width=0)

  def move_rectangle(self, x_coord, y_coord):
    self.canvas.moveto(self.rectangle, x_coord, y_coord)
  
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

  def fullscreen_process(self):
    print("Move the screen to the projected screen.")
    while sys.stdin.read(4) != "done":
      print("type 'done' to continue")
      sys.stdin.read(1)
    print("Begining experiment")
    self.make_call(self.activate_full_screen)

  
  def greyscale_intensity_experiment(self):
    self.fullscreen_process()
    
    for i in range(255, 0, -step):
      greyscale = "#" + "{:02x}".format(i)*3
      self.make_call(self.set_brightness, greyscale)
      #self.greyscale_intensity_readings.append([greyscale, self.power_meter.read()])
    self.make_call(self.destroy)
  
  def pixel_intensity_experiment(self):
    self.fullscreen_process()

    x_coords = np.linspace(0, self.canvas.winfo_screenwidth(), self.xNum, endpoint=False)
    y_coords = np.linspace(0, self.canvas.winfo_screenheight(), self.yNum, endpoint=False)

    #full_brightness_reading = self.power_meter.read()

    self.make_call(self.initialise_rectangle, x_coords[1], y_coords[1])

    for y_coord in y_coords:
      for x_coord in x_coords:
        self.make_call(self.move_rectangle, x_coord, y_coord)
        #self.intensity_readings[x_coord][y_coord] = full_brightness_reading - self.power_meter.read()
    self.make_call(self.destroy)


  


if __name__ == "__main__":
  screen = experimentGUI()
  screen.pixel_intensity_experiment_thread.start()
  screen.mainloop()

  #print(screen.intensity_readings)