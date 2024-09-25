import sys
# sys.path.append("C:\\Users\\whw29\\Desktop\\RCM\\RCM\\")

sys.path.append("../RCM/")
from OpticalPowerMeter import PM16_120
from light import DC2200

from threading import Event
from queue import Empty, Queue
import tkinter as tk
import numpy as np


class _CallData:
  '''
  Used to encapsulate the function and its argument sent from a daemon thread to the main thread to execute it in the main thread
  '''
  def __init__(self, fn, args, kwargs):
    self.fn = fn
    self.args = args
    self.kwargs = kwargs
    self.reply_event = Event()

class ExperimentGUI(tk.Tk):
  '''
  Opens a GUI that is displayed on the projector. Colors are inverted on the projector. Fullscreen only works only on Windows.

  :param exp_screen_res: resolution of the display of the projector
  :param greyscale: greyscale of the image on the main screen. Will be inverted on the projector, i.e. 255 is equivalent to 0
  :param do_overrideredirect: removes the taskbar and makes screen unresponsive, used to full-screen. 
  :param grid_layout: number of columns and rows of the screen. 1 is the minimum.
  '''
  def __init__(self, file_name="", exp_screen_res=(1920, 1080), greyscale=255, current_mA=100, do_overrideredirect=True, refresh_rate_ms=3, do_plot=True, use_stored_data=False):
    super().__init__()

    self.exp_screen_res = exp_screen_res
    self.do_plot = do_plot
    self.file_name = file_name
    self.background_power = 0

    if not use_stored_data:
      self.do_overrideredirect = do_overrideredirect
      self.refresh_rate_ms = refresh_rate_ms
      self.geometry("+0+0")
      self.title("Experiment")
      self.columnconfigure(0, weight=1)
      self.rowconfigure(0, weight=1)
      # Initialise canvas that will fill the whole window and expands if the window does
      self.canvas = tk.Canvas(self, bg=f"#{greyscale:02X}{greyscale:02X}{greyscale:02X}",highlightthickness=0)
      self.canvas.pack(fill="both", expand=True)

      # Initialise power meter
      self.power_meter = PM16_120()

      # Initialise light
      self.LED = DC2200()
      self.LED.set_current_mA(current_mA=current_mA)
      self.LED.on()

      # Create event queue
      self.request_queue = Queue()

  ## Normal Functions
  def activate_full_screen(self):
    '''
    Turns the window into a fullscreen

    :param do_overrideredirect: removes title menu but prevents screen from responding
    '''
    # Removes title menu so that screen is not obscured
    self.overrideredirect(self.do_overrideredirect)

    self.geometry('%dx%d%+d+%d'%(self.exp_screen_res[0], self.exp_screen_res[1], 0, 0))
  
  def _get_file_data(self, readings=[]):
    if self.file_name != "":
      data = []
      with open(self.file_name, "r") as file:
        lines = file.readlines()
        self.background_power = float(lines[0])
        for line in lines[1:]:
          data.append(line.split(","))
      return np.array(data, dtype=np.float32)
    elif readings != []:
      return np.array(readings, dtype=np.float32)
    else:
      print("No data available to plot!")
      return None
  
  def end_experiment(self):
    '''
    Destroys window
    '''
    self.destroy()
  
  ## Daemon Functions
  def call_handler(self):
    '''
    Runs every 500ms in the main event loop to check if a function run has been requested by the daemon threads
    '''
    try:
      # Checks the event queue
      data = self.request_queue.get_nowait()
      # Runs the function stored in the event queue
      data.fn(*data.args, *data.kwargs)
      data.reply_event.set()
    except Empty:
      pass

    # Reschedules this function to run again after 500ms
    self.after(self.refresh_rate_ms, self.call_handler)
  
  def make_call(self, fn, *args, **kwargs):
    '''
    Appends a function pointer and its arguments into the event queue
    '''
    # Creates an object to encapsulate the data
    data = _CallData(fn, args, kwargs)
    # Put onto event queue
    self.request_queue.put(data)
    data.reply_event.wait()