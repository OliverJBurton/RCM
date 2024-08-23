import tkinter as tk
from time import sleep
from threading import Thread, Event
from queue import Empty, Queue
#from OpticalPowerMeter import PM100
import sys
import customtkinter
import numpy as np
from PIL import ImageTk, Image
import os

class imageGUI(tk.Toplevel):
  def __init__(self, image_path, image_path_list):
    super().__init__()
    self.rowconfigure((0,1,2,3,4), weight=1, uniform="a")
    self.columnconfigure((0,1), weight=1)
    self.bind("<FocusOut>", self.destroy_window)
    self.title(image_path.split(".", 1)[0])

    self.image_path_list = image_path_list
    self.current_index = self.image_path_list.index(image_path)

    ## Image
    # Open image
    self.img = Image.open(image_path)
    # Get image dimensions
    self.img_width, self.img_height = self.img.size
    # Generate scaled Tk image with scaled dimensions w.r.t 500
    Tk_img = customtkinter.CTkImage(light_image=self.img, size=self.get_scaled_size(500))
    # Place image on window
    self.label = customtkinter.CTkLabel(self, image=Tk_img, text="")
    self.label.grid(column=0, columnspan=2, row=0, rowspan=4, sticky="nsew")
    # Refresh the image (to change to new image to if window size has changed) every 100 ms
    self.after(100, self.refresh_screen)

    ## Left button
    self.left_button = customtkinter.CTkButton(self, text="Previous image")
    self.left_button.grid(column=0, row=4, stick="nsew")
    self.left_button.bind("<ButtonRelease-1>", self.left_button_clicked)

    ## Right button
    self.right_button = customtkinter.CTkButton(self, text="Next image")
    self.right_button.grid(column=1, row=4, sticky="nsew")  
    self.right_button.bind("<ButtonRelease-1>", self.right_button_clicked)

  def get_scaled_size(self, dim):
    if self.img_height > self.img_width:
      scaled_size = (dim*self.img_width/self.img_height, dim)
    else:
      scaled_size = (dim, dim*self.img_height/self.img_width)
    return scaled_size

  def refresh_screen(self):
    if self.current_index == 0:
      self.left_button.configure(hover=False)
      self.left_button.configure(text="No previous image")
    elif self.current_index == len(self.image_path_list) - 1:
      self.right_button.configure(hover=False)
      self.right_button.configure(text="No next image")
    else:
      self.left_button.configure(hover=True)
      self.left_button.configure(text="Previous image")
      self.right_button.configure(hover=True)
      self.right_button.configure(text="Next image")
    self.label.update()
    new_Tk_img = customtkinter.CTkImage(light_image=self.img, size=(self.label.winfo_width(), self.label.winfo_height()))
    self.label.configure(image=new_Tk_img)
    self.after(100, self.refresh_screen)

  def left_button_clicked(self, event):
    if self.current_index == 0:
      return
    self.current_index -= 1
    self.img = Image.open(self.image_path_list[self.current_index])
  
  def right_button_clicked(self, event):
    if self.current_index == len(self.image_path_list) - 1:
      return
    self.current_index += 1
    self.img = Image.open(self.image_path_list[self.current_index])

  def destroy_window(self, event):
    self.destroy()

class imageDisplayGUI(tk.Tk):
  def __init__(self):  
    super().__init__()
    self.title("Image Display")
    self.image_screen = None
    self.geometry("800x600")
    self.num_columns = 3

    self.results_path_list = ["testing.png", "FoundationExamReceipt.png", "IntermediateExamReceipt.png", "RXSoftRockKitReceipt.png"]
    self.image_displayed = 0
    self.scrollable_frame = customtkinter.CTkScrollableFrame(self)
    self.scrollable_frame.pack(pady=10, padx=10, expand=True, fill="both")
    self.panel = customtkinter.CTkFrame(self.scrollable_frame)

    self.after(100, self.display_images())
    self.after(100, self.update_scrollable_frame)
  
  def update_scrollable_frame(self):
    self.scrollable_frame.update()
    new_width = self.scrollable_frame.winfo_width()
    if new_width < 500:
      new_num_columns = 1
    elif new_width < 750:
      new_num_columns = 2
    elif new_width < 1000:
      new_num_columns = 3
    else:
      new_num_columns = 4
    
    if self.num_columns != new_num_columns:
      self.num_columns = new_num_columns
      for child in self.scrollable_frame.winfo_children():
        child.destroy()
      self.image_displayed = 0
    
    self.after(500, self.update_scrollable_frame)
      
  def display_images(self):
    try:
      image_path = self.results_path_list[self.image_displayed]
      print("help")
      if self.image_displayed % self.num_columns == 0:
        self.panel = customtkinter.CTkFrame(self.scrollable_frame, width=200, height=200)
        self.panel.columnconfigure([i for i in range(self.num_columns)], weight=1, uniform="a")
        self.panel.pack(fill="x")
      img = customtkinter.CTkImage(light_image=Image.open(image_path), size=(200, 200))
      img_box = customtkinter.CTkLabel(self.panel, text=image_path, image=img, compound="bottom")
      img_box.grid(column = self.image_displayed % self.num_columns, row=self.image_displayed // self.num_columns, padx = 10, pady=10, sticky="nsew")
      img_box.bind("<Button-1>", self.open_image)
      self.image_displayed += 1
      if self.image_screen != None:
        self.image_screen.image_list = self.results_path_list
    except IndexError:
      pass
    self.after(100, self.display_images)
  
  def open_image(self, event):
    self.image_screen = imageGUI(event.widget.cget("text"), self.results_path_list)

class _CallData:
  def __init__(self, fn, args, kwargs):
    self.fn = fn
    self.args = args
    self.kwargs = kwargs

class experimentGUI(tk.Toplevel):
  def __init__(self, step=5, xNum=5, yNum=5):
    super().__init__()
    self.title("Experiment")
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
  screen2 = imageDisplayGUI()
  screen = experimentGUI()
  #screen.pixel_intensity_experiment_thread.start()
  screen.mainloop()

  #print(screen.intensity_readings)