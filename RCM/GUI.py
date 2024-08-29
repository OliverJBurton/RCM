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
import ctypes

class ImageGUI(tk.Toplevel):
  def __init__(self, image_path, image_path_list):
    super().__init__()
    self.title(image_path.split(".", 1)[0])
    # Set number of rows and columns
    self.rowconfigure((0,1,2,3,4), weight=1, uniform="a")
    self.columnconfigure((0,1), weight=1)
    # If window is no longer at the top, destroy it
    self.bind("<FocusOut>", self.destroy_window)

    self.image_path_list = image_path_list
    self.current_index = self.image_path_list.index(image_path)

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

    #Initialise left button
    self.left_button = customtkinter.CTkButton(self, text="Previous image")
    # Add to the 1st column and 5th row
    self.left_button.grid(column=0, row=4, stick="nsew")
    # Bind action when button is clicked
    self.left_button.bind("<ButtonRelease-1>", self.left_button_clicked)

    #Initalise Right button
    self.right_button = customtkinter.CTkButton(self, text="Next image")
    # Add to the 2nd column and 5th row
    self.right_button.grid(column=1, row=4, sticky="nsew")
    # Bind action when button is clicked 
    self.right_button.bind("<ButtonRelease-1>", self.right_button_clicked)

  def get_scaled_size(self, dim):
    '''
    Scales the image to size dim, the dimension with the smaller aspect is scaled down
    '''
    # Checks which aspect is larger
    if self.img_height > self.img_width:
      # If height is larger, make height dim while scaling down width
      scaled_size = (dim*self.img_width/self.img_height, dim)
    else:
      # If width is larger, make width dim while scaling down height
      scaled_size = (dim, dim*self.img_height/self.img_width)
    return scaled_size

  def refresh_screen(self):
    '''
    Reloads the screen to update the image and its size
    Updates the buttons if there is no previous or next image
    '''
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
    '''
    Updates the image being displayed to the previous one
    '''
    # If no previous image, nothing happens
    if self.current_index == 0:
      return
    # Update current image to previous one
    self.current_index -= 1
    self.img = Image.open(self.image_path_list[self.current_index])
  
  def right_button_clicked(self, event):
    '''
    Updates the image being displayed to the next one
    '''
    # If no next image, nothing happens
    if self.current_index == len(self.image_path_list) - 1:
      return
    # Update current image to next one
    self.current_index += 1
    self.img = Image.open(self.image_path_list[self.current_index])

  def destroy_window(self, event):
    '''Closes the window'''
    self.destroy()

class ImageDisplayGUI(tk.Tk):
  def __init__(self, image_path_list):  
    super().__init__()
    self.title("Image Display")
    self.geometry("800x600")

    # Opens up new window to display a single image
    self.image_screen = None
    # Number of columns the images will be arranged in
    self.num_columns = 3 

    # Path to image
    self.image_path_list = image_path_list #["testing.png", "FoundationExamReceipt.png", "IntermediateExamReceipt.png", "RXSoftRockKitReceipt.png"]
    # Number of images displayed
    self.image_displayed = 0
    # Enables scrolling
    self.scrollable_frame = customtkinter.CTkScrollableFrame(self)
    self.scrollable_frame.pack(pady=10, padx=10, expand=True, fill="both")
    self.panel = customtkinter.CTkFrame(self.scrollable_frame)

    self.after(100, self.display_images)
    self.after(100, self.update_scrollable_frame)
    self.mainloop()
  
  def update_scrollable_frame(self):
    '''
    Checks the width of the scrollable frame to determine the number of columns the images should be arranged in
    '''
    # Update frame to get current information
    self.scrollable_frame.update()
    # Get width of frame
    new_width = self.scrollable_frame.winfo_width()
    # Determine number of columns
    if new_width < 500:
      new_num_columns = 1
    elif new_width < 750:
      new_num_columns = 2
    elif new_width < 1000:
      new_num_columns = 3
    else:
      new_num_columns = 4
    
    # Ensure the required number of columns has changed
    if self.num_columns != new_num_columns:
      self.num_columns = new_num_columns
      
      # Destroys all the images in the scrollable frame so that display_images will update their arrangement
      for child in self.scrollable_frame.winfo_children():
        child.destroy()
      # Reset the number of images displayed
      self.image_displayed = 0
    
    self.after(500, self.update_scrollable_frame)
      
  def display_images(self):
    '''
    Displays all the images whose paths are stored, arranged in the correct number of columns
    '''
    try:
      image_path = self.image_path_list[self.image_displayed]

      # A frame is created for each row with the correct number of columns
      if self.image_displayed % self.num_columns == 0:
        # Initialise frame
        self.panel = customtkinter.CTkFrame(self.scrollable_frame, width=200, height=200)
        # Set number of columns in the frame
        self.panel.columnconfigure([i for i in range(self.num_columns)], weight=1, uniform="a")
        # Put the frame onto the scrollable frame such that it will fill up the width of the scrollable frame
        self.panel.pack(fill="x")
      # Create an image, resized to 200 by 200
      img = customtkinter.CTkImage(light_image=Image.open(image_path), size=(200, 200))
      # Create a label to display the image in
      img_box = customtkinter.CTkLabel(self.panel, text=image_path, image=img, compound="bottom")
      # Add image to current column and row
      img_box.grid(column = self.image_displayed % self.num_columns, row=self.image_displayed // self.num_columns, padx = 10, pady=10, sticky="nsew")
      # Bind action to open the image up with it is clicked
      img_box.bind("<Button-1>", self.open_image)
      self.image_displayed += 1
      # Update the image list in the image_screen window to allow traversing through all the images
      if self.image_screen != None:
        self.image_screen.image_list = self.image_path_list
    except IndexError:
      pass
    self.after(100, self.display_images)
  
  def open_image(self, event):
    '''
    Opens up window to display each image individually
    '''
    self.image_screen = ImageGUI(event.widget.cget("text"), self.image_path_list)

class _CallData:
  def __init__(self, fn, args, kwargs):
    self.fn = fn
    self.args = args
    self.kwargs = kwargs

class ExperimentGUI(tk.Tk):
  def __init__(self, step=5, xNum=5, yNum=5):
    super().__init__()
    self.overrideredirect(True)
    self.title("Experiment")
    self.columnconfigure(0, weight=1)
    self.rowconfigure(0, weight=1)
    # Initialise a white canvas
    self.canvas = tk.Canvas(self, bg="#FFFFFF", highlightthickness=0)
    # Make canvas fill the whole window and expand if the window expands
    self.canvas.pack(fill="both", expand=True)

    # Initialise power meter
    #self.power_meter = PM100()

    # Create event queue
    self.request_queue = Queue()

    # Pixel intensity experiment parameters
    self.xNum = xNum
    self.yNum = yNum
    self.rectangle = None
    self.intensity_readings = [[0 for i in range(self.yNum)] for j in range(self.xNum)]
    # Creates a daemon thread for the pixel intensity experiment to run in the background 
    self.pixel_intensity_experiment_thread = Thread(target=self.pixel_intensity_experiment, daemon=True)

    # Greyscale intensity experiment parameters
    self.step = step
    self.greyscale_intensity_readings = []
    # Creates a daemon thread for the greyscale intensity experiment to run in the background
    self.greyscale_intensity_experiment_thread = Thread(target=self.greyscale_intensity_experiment, daemon=True)

    # Checks the event queue every 500 ms
    self.after(500, self.call_handler)
    self.after(10, self.set_appwindow)

  def set_appwindow(self):
    GWL_EXSTYLE=-20
    WS_EX_APPWINDOW=0x00040000
    WS_EX_TOOLWINDOW=0x00000080
    hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    res = ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    self.wm_withdraw()
    self.after(10, lambda: root.wm_deiconify())

  def activate_full_screen(self):
    '''
    Turns the window into a fullscreen
    '''
    screen_height, screen_width = self.winfo_screenheight(), self.winfo_screenwidth()
    self.geometry('%dx%d%+d+%d'%(screen_width, screen_height, -screen_width, 0))

  def set_color(self, color):
    '''
    Sets the color of the canvas, used to adjust greyscale
    '''
    self.canvas.config(bg=color)

  def initialise_rectangle(self, width, height):
    '''
    Initialises a black rectangle and places it on the upper left hand corner of the canvas
    '''
    self.rectangle = self.canvas.create_rectangle(0, 0, width,height, fill="#000000", width=0)

  def move_rectangle(self, x_coord, y_coord):
    '''
    Moves the rectangle to the new coordinate (x_coord, y_coord)
    '''
    self.canvas.moveto(self.rectangle, x_coord, y_coord)
  
  def end_experiment(self):
    '''
    Destroys window
    '''
    self.destroy()

  def call_handler(self):
    '''
    Runs every 500ms in the main event loop to check if a function run has been requested by the daemon threads
    '''
    try:
      # Checks the event queue
      data = self.request_queue.get_nowait()
      # Runs the function stored in the event queue
      data.fn(*data.args, *data.kwargs)
    except Empty:
      pass

    # Reschedules this function to run again after 500ms
    self.after(500, self.call_handler)
  
  def make_call(self, fn, *args, **kwargs):
    '''
    Appends a function pointer and its arguments into the event queue
    '''
    # Creates an object to encapsulate the data
    data = _CallData(fn, args, kwargs)
    # Put onto event queue
    self.request_queue.put(data)

  def fullscreen_process(self):
    '''
    Tells the user to move the screen to where it'll be projected
    Upon confirmation, activate full screen
    '''
    print("Move the screen to the projected screen. Type 'done' to continue.")
    # Checks if the 4 characters of a line equals "done"
    while sys.stdin.read(4) != "done":
      print("type 'done' to continue")
      # Moves onto the next line to avoid reading the printed line
      sys.stdin.read(1)
    print("Begining experiment")
    # Request main thread to activate full screen
    self.make_call(self.activate_full_screen)

  def greyscale_intensity_experiment(self):
    '''
    Runs experiment to obtain relationship between greyscale of the image projected and the light intensity at the end of the microscope
    '''

    # Full screen
    self.fullscreen_process()
    
    # Loops through the greyscale range starting from white
    for i in range(255, 0, -self.step):
      # Formats the greyscale in #CCCCCC format
      greyscale = "#" + "{:02x}".format(i)*3
      # Request main thread to update the greyscale
      self.make_call(self.set_color, greyscale)
      # Take readings
      #self.greyscale_intensity_readings.append([greyscale, self.power_meter.read()])
    # Requests main thread to end experiment
    self.make_call(self.destroy)
  
  def pixel_intensity_experiment(self):
    '''
    Runs the experiment to determine how much each block of pixels contributes to the overall light intensity at the end of the microscope
    '''
    # Full screen
    self.fullscreen_process()

    # Create list of dimensions for the corner of each pixel block
    x_coords = np.linspace(0, self.canvas.winfo_screenwidth(), self.xNum, endpoint=False)
    y_coords = np.linspace(0, self.canvas.winfo_screenheight(), self.yNum, endpoint=False)

    # Measure total intensity of light
    #full_brightness_reading = self.power_meter.read()

    # Request main thread to initialise a block of darkened pixels
    self.make_call(self.initialise_rectangle, x_coords[1], y_coords[1])

    # Loop throguh the all possible locations of the pixel block
    for y_coord in y_coords:
      for x_coord in x_coords:
        # Request main thread to move the block of darkened pixels
        self.make_call(self.move_rectangle, x_coord, y_coord)
        # Record change in intensity 
        #self.intensity_readings[x_coord][y_coord] = full_brightness_reading - self.power_meter.read()
    # Request main thread to end experiment
    self.make_call(self.destroy)
  
if __name__ == "__main__":
  # screen1 = ImageDisplayGUI()
  screen2 = ExperimentGUI()
  screen2.pixel_intensity_experiment_thread.start()
  screen2.mainloop()

  #print(screen.intensity_readings)