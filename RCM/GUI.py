import time
import random
from PIL import Image

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

import tkinter as tk
import customtkinter

from threading import Thread, Event
from queue import Empty, Queue

from OpticalPowerMeter import PM16_120
from light import DC2200



"""
Note resolution of experiment screen is 1920 x 1080
Note greyscale is inverted on the projector to that on the main screen

To open a blank black (on the projector, appears white on the main screen) screen that you can move around, do:
screen = DebugScreen()
screen.mainloop()

"""

class _ImageGUI(tk.Toplevel):
  '''
  Pop-up window that displays an image in a larger size
  Can navigate through the gallery of images
  '''
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
  '''
  Image gallery, can click on each image to expand image

  :param image_path_list: a list of paths to the images to be displayed on the gallery
  '''
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

    # Update image displayed in gallery
    self.after(100, self.display_images)
    # Updates number of columns the photos are displayed in if window size has changed
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
    self.image_screen = _ImageGUI(event.widget.cget("text"), self.image_path_list)

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
  def __init__(self, exp_screen_res=(1920, 1080), greyscale=255, do_overrideredirect=True, refresh_rate_ms=3, do_plot=True):
    super().__init__()

    self.geometry("+0+0")
    self.exp_screen_res = exp_screen_res
    self.do_overrideredirect = do_overrideredirect
    self.refresh_rate_ms = refresh_rate_ms
    self.do_plot = do_plot

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
    self.LED.set_current_mA(current_mA=100)
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
  
  def end_experiment(self):
    '''
    Destroys window
    '''
    self.LED.close()
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
  def take_measurement(self):
    print(self.power_meter.get_power_reading_W_str())

class DebugScreen(ExperimentGUI):
  def __init__(self, greyscale=255, do_overrideredirect=True):
    super().__init__(greyscale=greyscale, do_overrideredirect=do_overrideredirect)
    print("Press 'f' to move screen to projector monitor and activate full screen")
    print("Press 'l' to obtain reading from power meter")
    print("Press 'e' to end experiment")

    self.bind("<Key>", self.key_press)
  
  def key_press(self, event):
    if event.char == "l":
      print(self.power_meter.get_power_reading_W_str())
    elif event.char == "f":
      self.activate_full_screen()
    elif event.char == "e":
      self.destroy()

class GreyScaleEnergyExperiment(ExperimentGUI):
  '''
  Determine the relationship between energy of light on the sample with respect to the greyscale of the image taken by the camera

  :param step: the interval between greyscale values wherein measurements are taken
  '''

  def __init__(self, fileName="greyscale_energy_readings.txt", do_plot=True):
    super().__init__(greyscale=0, do_plot=do_plot)

    self.fileName = fileName

    # Greyscale energy experiment parameters
    self.greyscale_energy_readings = []
    self.background_energy = 0
    # Creates a daemon thread for the greyscale energy experiment to run in the background
    self.greyscale_energy_experiment_thread = Thread(target=self.greyscale_energy_experiment, daemon=True)

    self.after(self.refresh_rate_ms, self.call_handler)

  def set_greyscale(self, greyscale):
    '''
    Sets the luminance of the greyscale background image
    '''
    self.canvas.config(bg=f"#{greyscale:02X}{greyscale:02X}{greyscale:02X}")

  def greyscale_energy_experiment(self):
    '''
    Runs experiment to obtain relationship between greyscale of the image projected and the light energy at the end of the microscope
    Writes data to file called greyscale_energy_readings.txt (by default)
    '''

    print("Begin Experiment")

    # Full screen and wait until full screen process is finished
    self.make_call(self.activate_full_screen)
    time.sleep(1)
    self.background_energy = float(self.power_meter.get_power_reading_W_str())

    # Loops through the greyscale range starting from white
    for i in range(0, 255, 1):
      # Request main thread to update the greyscale
      self.make_call(self.set_greyscale, i)
      # Take readings
      self.greyscale_energy_readings.append([i, float(self.power_meter.get_power_reading_W_str())])

    # Write to file
    with open(self.fileName, "w") as file:
      file.write(f"{self.background_energy}\n")
      for reading in self.greyscale_energy_readings:
        file.write(f"{reading[0]},{reading[1]}\n")

    # Requests main thread to end experiment
    print("End Experiment")
    self.make_call(self.destroy)

  def plot_and_fit_greyscale_energy(self, order=2):
    '''
    Plots and fits a polynomial to the light energy against the greyscale. Data taken from textfile or from self.greyscale_energy_readings

    :param fileName: name of textfile storing the data.
    :param order: order of the polynomial fitted
    '''
    if self.fileName != "":
      data = []
      with open(self.fileName, "r") as file:
        lines = file.readlines()
        self.background_energy = float(lines[0])
        for line in lines[1:]:
          data.append(list(line.split(",")))
      data = np.array(data, dtype=np.float32)
    elif self.greyscale_energy_readings != []:
      data = np.array(self.greyscale_energy_readings, dtype=np.float32)
    else:
      print("No data available to plot!")
      return

    greyscale, energy_proportion = data[:,0], data[:,1]/np.max(data[:,1])
    
    parameters = np.polyfit(greyscale, energy_proportion, order)
    energy_function_of_greyscale = np.poly1d(parameters)

    parameters = np.polyfit(energy_proportion, greyscale, order)
    greyscale_function_of_energy = np.poly1d(parameters)

    if self.do_plot:
      plt.plot(greyscale, energy_proportion, 'rx', greyscale, energy_function_of_greyscale(greyscale))
      plt.xlim((greyscale[0], greyscale[-1]))
      plt.ylim(bottom=np.min(energy_proportion))
      plt.xlabel("Greyscale")
      plt.ylabel("G")
      plt.show()

    return energy_function_of_greyscale, greyscale_function_of_energy

class PixelEnergyExperiment(ExperimentGUI):
  '''
  Determines how much light energy each pixel contributes to the sample

  :param kernel_dim: dimension of the kernel moved across the display
  :param scale: effectively reduces the resolution of the display by 8 in both dimension, reduces time for experiment to complete

  '''
  def __init__(self, kernel_dim=(60, 60), fileName="pixel_energy_readings.txt", do_plot=True):
    super().__init__(greyscale=0, do_plot=do_plot)

    self.fileName = fileName

    # Pixel energy experiment parameters
    self.kernel_dim = kernel_dim
    self.energy_readings = []
    self.background_energy = 0
    # Creates a daemon thread for the pixel energy experiment to run in the background 
    self.pixel_energy_experiment_thread = Thread(target=self.pixel_energy_experiment, daemon=True)

    self.after(self.refresh_rate_ms, self.call_handler)

  def create_rectangle(self):
    """
    Creates a rectangle in the upper left hand corner of the screen
    """
    self.rectangle = self.canvas.create_rectangle(0, 0, self.kernel_dim[0], self.kernel_dim[1], fill="#FFFFFF", width=0)

  def move_rectangle(self, x_coord, y_coord):
    '''
    Moves the rectangle to the new coordinate (x_coord, y_coord)
    '''
    self.canvas.moveto(self.rectangle, x_coord, y_coord)
  
  def pixel_energy_experiment(self):
    '''
    Runs the experiment to determine how much each block of pixels contributes to the overall light energy at the end of the microscope
    Stores data in text file called pixel_energy_readings.txt
    '''

    print("Begin Experiment")

    # Full screen and wait until full screen process is completed
    self.make_call(self.activate_full_screen)
    time.sleep(1)

    # Create list of dimensions for the corner of each pixel block, additional +1 as upper bound is included
    x_coords = np.arange(0, self.exp_screen_res[0], step=self.kernel_dim[0], dtype=int)
    y_coords = np.arange(0, self.exp_screen_res[1], step=self.kernel_dim[1], dtype=int)

    # Loop through the all possible locations of the pixel block
    with open(self.fileName, "w") as file:
      self.background_energy = float(self.power_meter.get_power_reading_W_str())
      print(self.background_energy)
      file.write(f"{self.background_energy}\n")
      self.make_call(self.create_rectangle)
      for y_coord in y_coords:
        # To store a width of energy values
        temp = []
        for x_coord in x_coords:
          # Request main thread to move the block of darkened pixels
          self.make_call(self.move_rectangle, x_coord, y_coord)

          temp.append(self.power_meter.get_power_reading_W_str())
          # Write data to textfile
        file.write(",".join(temp) + "\n")

        self.energy_readings.append(temp)
    file.close()

    # Request main thread to end experiment
    print("End Experiment")
    self.make_call(self.destroy)

  def _get_file_data(self):
    if self.fileName != "":
      data = []
      with open(self.fileName, "r") as file:
        lines = file.readlines()
        self.background_energy = float(lines[0])
        for line in lines[1:]:
          data.append(list(line.split(","))[:-1])
      return np.array(data, dtype=np.float32)
    elif self.energy_readings != []:
      return np.array(self.energy_readings, dtype=np.float32)
    else:
      print("No data available to plot!")
      return None

  def plot_pixel_energy_fraction(self):
    '''
    Use data stored in file or variable self.energy_readings to plot. Each point is a fraction of the total light energy.
    '''
    data = self._get_file_data()

    plt.contourf( data, levels=30, cmap="RdGy")
    plt.colorbar()
    plt.show()

  def interpolate_data(self):
    data = self._get_file_data()

    M, N = data.shape
    x = np.arange(M)
    y = np.arange(N)
    interp = RegularGridInterpolator([x, y], data)

    # Create Matrix with size equal to resolution of projector screen
    xx = np.linspace(0, M-1, self.exp_screen_res[0])
    yy = np.linspace(0, N-1, self.exp_screen_res[1])
    X, Y = np.meshgrid(xx, yy, indexing="ij")

    # Interpolated array of f_x_y for all pixels on the projector screen
    Z = interp((X, Y))
    
    if self.do_plot:
      plt.contourf(Z, levels=30, cmap="RdGy")
      plt.colorbar()
      plt.show()

    return Z

class LightIntensityDetermination:
  """
  Performs the greyscale energy and pixel energy experiment to determine the required greyscale to project the desired light intensity on a point on the sample

  :param kernel_dim: size of the kernels used in the pixel energy experiment
  :param do_plot: plot figures of the result of both experiments
  """
  def __init__(self, image_path="", kernel_dim=(60,60), do_plot=True, use_stored_data=False):
    """
    Rescaling equation
    E_xy: energy of pixel at position (x, y)
    E_max_xy: maximum energy of pixel at position (x, y)
    B_xy: background energy of pixel at position (x, y)
    min_E_max: smallest maximum energy of all the pixels (pixel with this energy is the limiting pixel)
    min_B: background energy of the limiting pixel

    corrected_E - min_B = (E_xy - B_xy) / (E_max_xy - B_xy) * (min_E_max - min_B)
    
    """

    # Deal with zero values

    # Obtain relationship between greyscale and light energy
    experiment1 = GreyScaleEnergyExperiment(do_plot=do_plot)
    if not use_stored_data:
      experiment1.greyscale_energy_experiment_thread.start()
      experiment1.mainloop()
    else:
      experiment1.end_experiment()

    self.energy_function_of_greyscale, self.greyscale_function_of_energy = experiment1.plot_and_fit_greyscale_energy()

    # Obtain f(x, y): 
    experiment2 = PixelEnergyExperiment(kernel_dim=kernel_dim, do_plot=do_plot)
    if not use_stored_data:
      experiment2.pixel_energy_experiment_thread.start()
      experiment2.mainloop()
    else:
      experiment2.end_experiment()

    # Add cutoff
    self.f_x_y = experiment2.interpolate_data() # Also is max energy array
    self.exp_screen_res = experiment2.exp_screen_res

    # Open image in greyscale mode, scale it to resolution of projector screen
    # Possible error could arise if image as a transparency channel
    # image_array = np.asarray(Image.open(image_path).convert("L"))
    np.set_printoptions(threshold=np.inf)
    image_array = np.reshape(self.open_scale_image(image_path), self.exp_screen_res)

    # Determines what the image would look like without any correction
    energy_array = self.energy_function_of_greyscale(image_array) * self.f_x_y
    background_energy_array = self.energy_function_of_greyscale(0) * self.f_x_y
    min_energy_max = np.min(self.f_x_y[:,120:-1])
    min_background_energy = np.min(background_energy_array[:,120:-1])

    # print(min_energy_max)
    # print(np.max(self.f_x_y))
    # print(min_background_energy)
    # print(np.max(background_energy_array))

    # Apply rescaling
    corrected_energy_array = (energy_array - background_energy_array) / (self.f_x_y - background_energy_array) * (min_energy_max - min_background_energy) + min_background_energy

    corrected_greyscale_array = np.round(np.reshape(self.greyscale_function_of_energy(corrected_energy_array/self.f_x_y), self.exp_screen_res[::-1] +(1,))).astype(np.uint8)
    corrected_rgb_array = np.repeat(corrected_greyscale_array, 3, axis=2)
    print(corrected_rgb_array.shape)

    corrected_image = Image.fromarray(corrected_rgb_array, "RGB")
    corrected_image.show()
    corrected_image_path = f"{image_path.split(".")[0]}_corrected.{image_path.split(".")[1]}"
    corrected_image.save(corrected_image_path)

  def open_scale_image(self, image_path):
    """
    Opens image, scales it to the resolution of the projector screen, padding missing parts

    :param image_path: path to the image
    :returns: numpy array of the padded, rescaled image

    """

    # Opens image and converts it into greyscale mode
    image = Image.open(image_path).convert("L")
    image_dim = image.size

    # Determine which dimension to scale up
    width_resize_factor = self.exp_screen_res[0] / image_dim[0]
    if image_dim[1] * width_resize_factor > self.exp_screen_res[1]:
      height_resize_factor = self.exp_screen_res[1] / image_dim[1]
      new_size = (int(image_dim[0] * height_resize_factor), self.exp_screen_res[1])
    else:
      new_size = (self.exp_screen_res[0], int(image_dim[1] * width_resize_factor))

    offset = ((self.exp_screen_res[0] - new_size[0]) // 2, (self.exp_screen_res[1] - new_size[1]) // 2)
    scaled_image = image.resize(new_size)

    # Creates a new black image with resolution of the projector screen
    # Paste the scaled_image with an offset from the top left corner to put it in the center
    padded_rescaled_image = Image.new(scaled_image.mode, self.exp_screen_res, 0)
    padded_rescaled_image.paste(scaled_image, offset)
    padded_rescaled_image.show()

    return np.asarray(padded_rescaled_image)


# Time per measurement approximately 62.53 ms
if __name__ == "__main__":
  # screen = DebugScreen(greyscale=0)
  # screen.mainloop()
  # screen = GreyScaleEnergyExperiment()
  # screen.greyscale_energy_experiment_thread.start()
  # screen.mainloop()
  # screen.plot_and_fit_greyscale_energy()

  # experiment = PixelEnergyExperiment(kernel_dim=(60, 60))
  # experiment.pixel_energy_experiment_thread.start()
  # experiment.mainloop()
  # experiment.plot_pixel_energy_fraction()
  # experiment.interpolate_data()

  # screen = LightIntensityDetermination()

  screen = LightIntensityDetermination(image_path="C:\\Users\\whw29\\Desktop\\test.png", do_plot=False, use_stored_data=True)









class ParticleGrowthExperiment(ExperimentGUI):
  """

  Creates the required grid of rectangles on the screen with required intensities on the sample

  :param seed: seed to generates coordinates
  :param grid_layout: tuple of the number of grids in each dimension
  :param padding: padding within each grid to control spacing between each rectangle
  :param num_points: number of rectangles to generate
  :param intensities: list of intensities required at each rectangle
  :param kernel_dim: dimension of the kernel used in pixel energy experiment
  :param do_plot: True to plot figures for grey scale energy and pixel energy experiment

  """
  def __init__(self, seed="Miaow", grid_layout=(80, 60), padding=(10, 10), num_points=10, intensities=[], kernel_dim=(60, 60), do_plot=True):
    super().__init__()
    self.grid_dim = (self.exp_screen_res[0]//grid_layout[0], self.exp_screen_res[1]//grid_layout[1])
    self.grid_coordinates = []
    self.corner_coordinates = []
    self.intensities = intensities
    self.greyscale = []

    # Generate a number of non-overlapping grid locations
    random.seed(seed)
    while len(self.corner_coordinates) != num_points:
      potential_grid = (random.randint(0, grid_layout[0]), random.randint(0, grid_layout[1]))
      if potential_grid not in self.grid_coordinates:
        self.grid_coordinates.append(potential_grid)
        self.corner_coordinates.append((potential_grid[0]*self.grid_dim[0], potential_grid[1]*self.grid_dim[1]))

    # Perform experiment to determine greyscale values to obtain the desired intensities at different points
    setup = LightIntensityDetermination(kernel_dim=kernel_dim, do_plot=do_plot)

    for i, corner_coordinate in enumerate(self.corner_coordinates):
      self.greyscale.append(setup.obtain_required_greyscale(wanted_light_intensity=self.intensities[i], grid_dim=self.grid_dim, corner_coord=corner_coordinate))
    
    # Start display, create rectangles with required greyscale in each position

    for i, corner_coordinate in enumerate(self.corner_coordinates):
      self.canvas.create_rectangle(corner_coordinate[0]+padding[0],
      corner_coordinate[1] + padding[1],
      corner_coordinate[0] + self.grid_dim[0] - padding[0],
      corner_coordinate[1] + self.grid_dim[1] - padding[1],
      fill=f"#{self.greyscale[i]:02X}{self.greyscale[i]:02X}{self.greyscale[i]:02X}")