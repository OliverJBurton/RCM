import glob
from PIL import Image
import numpy as np
import re
import matplotlib.pyplot as plt
from matplotlib import rcParams, cycler
from threading import Event, Thread
import time
from datetime import datetime

"""
Assumes all images have the png extension
Assumes image name follows this convention: 'image_cap_' + {index} + '_' + {wavelength} + '_' + {time} + '_img.png'

Usage example, doing image processing and displaying results: 
processing = AveragePowerOverTimeAndWavelength(save_file="/Users/edwardwei/Documents/RCM/Image Processing/average_power_Au2.txt")
processing.get_average_count()
processing.plot_blocks_over_time_at_wavelength()

Usage example, displaying stored data:
processing = AveragePowerOverTimeAndWavelength(save_file="/Users/edwardwei/Documents/RCM/Image Processing/average_power_Au2.txt")
processing.retrieve_data()
processing.plot_blocks_over_time_at_wavelength()

"""

rcParams["axes.prop_cycle"] = cycler(color=['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'purple', 'pink', 'brown', 'orange', 'teal', 'coral', 'lightblue', 'lime', 'lavender', 'turquoise', 'darkgreen', 'tan', 'salmon', 'gold'])


class AveragePowerOverTimeAndWavelength:
  """
  Performs image processing: extract blocks from the image, normalise then average the blocks.
  Provides a thread to perform processing while the experiment is performed

  :param image_folder: folder of images to perform processing on
  :param save_file: name of text file to store data in
  :param thread_sleep_time: how much time the thead waits before checking if new images have been taken
  :param allowed_wavelengths: list of wavelengths to keep

  self.blocks stores the blocks dimension in this format: [top left corner x, width, top left corner y, height]
  
  """
  def __init__(self, image_folder="../../Downloads/Images4/Images4", 
  save_file = "average_power_over_wavelength_and_time.txt", thread_sleep_time=120,
  allowed_wavelengths=[420.0, 436.0, 453.0, 469.0, 485.0, 502.0, 518.0, 534.0, 551.0, 567.0, 583.0, 599.0, 616.0, 632.0, 648.0, 665.0, 681.0, 697.0, 714.0, 730.0]):
    
    self.image_folder = image_folder
    self.save_file = save_file
    self.allowed_wavelengths = allowed_wavelengths
    self.thread_sleep_time = thread_sleep_time
    self.is_finished = Event()
    self.taking_images = Event()
    self.times = []
    self.wavelengths = []
    self.counts = []
    self.blocks = [[3180, 548, 0, 160], [2235, 813, 0, 201], [1350, 798, 0, 219], [453, 816, 0, 228],
                   [3164, 552, 324, 504], [2268, 744, 320, 532],[1364, 744, 340, 528],[540, 688, 372, 452],
                   [3140, 196, 972, 508], [2268, 736, 1012, 524],[1364, 752, 1000, 556],[796, 452, 1012, 552]]
    self.n_dim = [1640, 2136, 1840, 532]
    # self.blocks = [[453, 816, 0, 228], [1350, 798, 0, 219], [2235, 813, 0, 201], [3141, 639, 0, 168],
    #                [428, 808, 344, 540], [1364, 744, 340, 528], [2268, 744, 320, 532], [3164, 552, 324, 504],
    #                [412, 836, 1012, 552], [1364, 752, 1000, 556], [2268, 736, 1012, 524], [3144, 500, 988, 504]]

    self.average_count_thread = Thread(target=self.average_count_irt)

  def average_count_irt(self):
    """
    Thread to perform image processing - extracting blocks of different greyscale, normalising then averaging each block - while experiment is carried out. Stores the data in a file.
    """

    # list to store images already processed
    image_path_list = []
    # Clear file of data
    self.save_data()

    while True:
      # Wait 2 minutes
      time.sleep(self.thread_sleep_time)

      # Only perform data processing when images are not being taken
      if not self.taking_images.is_set():
        
        # Retrieve stored data
        self.retrieve_data()
        average_count_dict = dict(zip(self.wavelengths, self.counts))

        # Retrieve newly added images
        new_image_list = []
        for filename in glob.glob(f"{self.image_folder}/*.png"):
          if not (filename in image_path_list):
            image_path_list.append(filename)
            new_image_list.append(filename)

        # Leave if there are no new images and the experiment has ended
        if new_image_list == [] and self.is_finished.is_set():
          return

        # Sort images in ascending order of wavelength and time
        """See https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/"""
        new_image_list = sorted(new_image_list, key=lambda string_ : [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)])

        # Normalise then average each block of data
        self._process_data(new_image_list, average_count_dict)

  def get_average_count(self):
    """
    Performs image processing - extracting blocks of different greyscale, normalising then averaging each block. The data is stored in a file. 
    """
    # Get all image file names
    image_path_list = []
    for filename in glob.glob(f"{self.image_folder}/*.png"):
      image_path_list.append(filename)
    
    # Filter out unwanted wavelengths and sort images in ascending order of wavelength and time
    """See https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/"""
    image_path_list = [path for path in image_path_list if float(path.split("_")[3]) in self.allowed_wavelengths]
    image_path_list = sorted(image_path_list, key=lambda string_ : [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)])

    average_count_dict = {}
    self._process_data(image_path_list, average_count_dict)

  def _process_data(self, image_path_list, average_count_dict):
    # Create dictionary to store a list of the first images of each greyscale block for each wavelength
    first_dict = {}
    for filename in image_path_list:
      print(filename)

      # Extract time data 
      time = float(filename.split("_")[4])
      if time not in self.times:
        self.times.append(float(filename.split("_")[4]))

      # Extract blocks 
      image_array = np.asarray(Image.open(filename))
      if self.blocks == []:
        block_list = [image_array]
      else:
        block_list = []
        for block in self.blocks:
          block_list.append(image_array[block[2]:block[2]+block[3], block[0]:block[0]+block[1]])
      
      # Use spot where no UV light has incident as normalising block
      # normalising_block = np.average(image_array[self.n_dim[0]:self.n_dim[0]+self.n_dim[1], self.n_dim[2]: self.n_dim[2]+self.n_dim[3]])

      # Check wavelength of file, if not seen before, add it to the dictionary
      # Images averaged then normalised
      wavelength = float(filename.split("_")[3])
      if wavelength not in average_count_dict.keys():
        first_dict[wavelength] = block_list
        average_count_dict[wavelength] = [[1.0 for block_data in block_list]]
        # average_count_dict[wavelength] = [[block_data/normalising_block for block_data in block_list]]
      else:
        average_normalised_block_list = [np.average(block_list[i]/first_block) for i, first_block in enumerate(first_dict[wavelength])] 
        average_count_dict[wavelength].append(average_normalised_block_list)
        # average_count_dict[wavelength].append([block_data/normalising_block for block_data in block_list])

    self.wavelengths = list(average_count_dict.keys())
    self.counts = list(average_count_dict.values())
    self.save_data()

  def _check_data(self):
    # Determines which wavelength has missing data points or are completely absent
    delete_index = []
    for i, count_over_time in enumerate(self.counts):
      if len(count_over_time) != len(self.times):
        print(f"Images of wavelength {self.wavelengths[i]} are missing data points! Only {len(count_over_time)} out of {len(self.times)} are available.")
        delete_index.append(i)
    
    self.wavelengths = [wavelength for i, wavelength in enumerate(self.wavelengths) if i not in delete_index]
    self.counts = [count_over_time for i, count_over_time in enumerate(self.counts) if i not in delete_index]
    
    for wavelength in self.allowed_wavelengths:
      if wavelength not in self.wavelengths:
        print(f"Images with wavelength {wavelength} are missing from the list!")

  def save_data(self):
    """
    Storage structure:
      line 1: times separated by commas
      line 2: wavelengths separated by commas
      line 3 onwards: every line is the data collected from each wavelength
                      every chunk separated by '|' represents data collected at each time
                      every element in each chunk is separated by "," represents data collected from a block
    """
    with open(self.save_file, "w") as file:
      for time in self.times:
        file.write(f"{time},")
      file.write("\n")

      for wavelength in self.wavelengths:
        file.write(f"{wavelength},")
      file.write("\n")

      for count_list in self.counts:
        for count in count_list:
          for block in count:
            file.write(f"{block},")
          file.write("|")
        file.write("\n")

  def retrieve_data(self):
    """
    Retrieves data from required format and stores the data in lists
    Keeps allowed wavelengths
    """

    with open(self.save_file, "r") as file:
      data = file.readlines()
      self.times = [float(time) for time in data[0].split(",")[:-1]]
      self.wavelengths = [float(wavelength) for wavelength in data[1].split(",")[:-1]]
      for count_list in data[2:]:
          self.counts.append([[float(data) for data in count.split(",")[:-1]] for count in count_list.split("|")[:-1]])

    self.counts = [count for count, wavelength in zip(self.counts, self.wavelengths) if wavelength in self.allowed_wavelengths]
    self.wavelengths = [wavelength for wavelength in self.wavelengths if wavelength in self.allowed_wavelengths]

  def plot_blocks_over_time_at_wavelength(self, wavelength=730.0):
    """
    Displays the change in transmission of each block at a specified wavelength over time 

    :param wavelength: the specified wavelength
    """

    # Filters out incomplete data
    self._check_data()

    n_counts = np.array(self.counts, np.float32)
    index = self.wavelengths.index(wavelength)
    num_blocks = len(self.blocks)

    for i in range(num_blocks):
      plt.plot(np.array(self.times)/60, n_counts[index,:,i].T)
    plt.legend(np.arange(num_blocks))
    plt.xlabel("Time (minutes)")
    plt.ylabel("Average Normalised Count")
    plt.show()

  def plot_data_block_of_nth_brightness(self, n=1):
    """
    Displays the change in transmission of each block in 2 plots, one at each wavelength and one over time.

    :param n: assuming self.blocks is arranged in descending order of greyscale, n is the nth brightest block (or nth block in the list)
    """
    self._check_data()
    n_counts = np.array(self.counts, np.float32)

    # Creates 2 plots aranged in 2 columns
    fig, ax = plt.subplots(1, 2)
    # Plots power for each wavelength
    ax[0].plot(self.wavelengths, n_counts[:,:,n-1], "x")
    ax[0].legend(self.times)
    ax[0].set_xlabel("Wavelength (nm)")
    ax[0].set_ylabel("Average Count")

    # Plots power as it changes with time
    # Each row corresponds to each time, hence must transpose array
    ax[1].plot(np.array(self.times) / 60, n_counts[:,:,n-1].T)
    ax[1].legend(self.wavelengths)
    ax[1].set_xlabel("Time (minute)")
    ax[1].set_ylabel("Average Count")

    plt.show()
  
  def plot_peak_wavelength_over_time(self):
    self._check_data()
    n_counts = np.array(self.counts, np.float32)
    num_blocks = len(self.blocks)

    for i in range(num_blocks):
      max_index = np.argmin(n_counts[:,:,i], axis=0)
      max_wavelength_over_time = [self.wavelengths[index] for index in max_index]
      plt.plot(np.array(self.times) / 60, max_wavelength_over_time, "x")
    plt.legend(np.arange(num_blocks))
    plt.xlabel("Time (minutes)")
    plt.ylabel("Max average Normalised Count")
    plt.show()



if __name__ == "__main__":
  # filename = "../../Downloads/Images4/Images4/image_cap_19_730.0_72450_img.png"
  # image_array = np.asarray(Image.open(filename)).copy()
  # image_array[0:160,3180:3180+548] = 0
  # plt.imshow(image_array)
  # plt.show()
  processing = AveragePowerOverTimeAndWavelength(save_file="/Users/edwardwei/Documents/RCM/Image Processing/average_power_Au2.txt")
  processing.retrieve_data()
  processing.plot_peak_wavelength_over_time()
  # processing.plot_blocks_over_time_at_wavelength(583.0)
