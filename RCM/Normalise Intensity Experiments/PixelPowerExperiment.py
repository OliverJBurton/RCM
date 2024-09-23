import ExperimentGUI

class PixelPowerExperiment(ExperimentGUI):
  '''
  Determines how much light power each pixel contributes to the sample

  :param kernel_dim: dimension of the kernel moved across the display
  :param scale: effectively reduces the resolution of the display by 8 in both dimension, reduces time for experiment to complete

  '''
  def __init__(self, kernel_dim=(60, 60), file_name="pixel_power_readings.txt", image_path="", current_mA=100, do_plot=True):
    super().__init__(file_name=file_name, current_mA=current_mA, do_plot=do_plot)

    # Create image 
    self.image_path = image_path
    if self.image_path != "":
      bg_img = ImageTk.PhotoImage(Image.open(self.image_path))
      self.canvas.bg_img = bg_img
      self.canvas.create_image((0, 0), image=self.canvas.bg_img, anchor="nw")
    
    # Set up grid of rectangles, gets background reading, then set first rectangle to be transparent
    self.rectangles_list = []
    for row in range(0, self.exp_screen_res[1], kernel_dim[1]):
      for column in range(0, self.exp_screen_res[0], kernel_dim[0]):
        self.rectangles_list.append(self.canvas.create_rectangle(column, row, column+kernel_dim[0], row+kernel_dim[1], fill="#000000", width=0))

    # Pixel power experiment parameters
    self.kernel_dim = kernel_dim
    self.power_readings = []

    # Creates a daemon thread for the pixel power experiment to run in the background 
    self.pixel_power_experiment_thread = Thread(target=self.pixel_power_experiment, daemon=True)

    self.after(self.refresh_rate_ms, self.call_handler)

  def move_hole(self, i):
    '''
    Sets rectangle at index i to be transparent, sets previous rectangle to be black
    '''
    self.canvas.itemconfig(self.rectangles_list[i], fill="")
    self.canvas.itemconfig(self.rectangles_list[i-1], fill="#000000")
  
  def pixel_power_experiment(self):
    '''
    Runs the experiment to determine how much each block of pixels contributes to the overall light power at the end of the microscope
    By default, stores data in text file called pixel_power_readings.txt
    '''

    print("Begin Experiment")

    self.activate_full_screen()
    time.sleep(1)

    # Loop through the all possible locations of the pixel block
    self.background_power = float(self.power_meter.get_power_reading_W_str())
    print(f"The background power is: {self.background_power} W")

    for i in range(len(self.rectangles_list)):
      self.make_call(self.move_hole, i)
      self.power_readings.append(self.power_meter.get_power_reading_W_str())

    # Write to file
    with open(self.file_name, "w") as file:
      file.write(f"{self.background_power}\n")
      for reading in self.power_readings:
        file.write(f"{reading}\n")

    # Request main thread to end experiment
    print("End Experiment")
    self.make_call(self.destroy)

  def plot_pixel_power_fraction(self):
    '''
    Use data stored in file or variable self.power_readings to plot. Each point is a fraction of the total light power.
    '''
    data = super()._get_file_data(readings=self.power_readings).reshape((self.exp_screen_res[1]//self.kernel_dim[1], self.exp_screen_res[0]//self.kernel_dim[0]))

    plt.contourf(data, levels=30, cmap="RdGy")
    plt.colorbar()
    plt.show()

  def interpolate_data(self):
    data = super()._get_file_data(readings=self.power_readings).reshape((self.exp_screen_res[1]//self.kernel_dim[1], self.exp_screen_res[0]//self.kernel_dim[0])) / self.kernel_dim[0] / self.kernel_dim[1]

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