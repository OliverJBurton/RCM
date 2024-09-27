import glob
from PIL import Image
import numpy as np
import re
import matplotlib.pyplot as plt
from threading import Event, Thread
import time
from datetime import datetime

"""
Assumes all images have the png extension
Assumes image name follows this convention: 'image_cap_' + {index} + '_' + {wavelength} + '_' + {time} + '_img.png'
"""


class AveragePowerOverTimeAndWavelength:
  def __init__(self, image_folder="../../../Downloads/Images", 
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
    self.blocks = [[3141, 639, 0, 168], [2235, 813, 0, 201], [1350, 798, 0, 219], [453, 816, 0, 228],
                   [3164, 552, 324, 504], [2268, 744, 320, 532],[1364, 744, 340, 528],[428, 808, 344, 540],
                   [3144, 500, 988, 504], [2268, 736, 1012, 524],[1364, 752, 1000, 556],[412, 836, 1012, 552]]
    # self.blocks = [[453, 816, 0, 228], [1350, 798, 0, 219], [2235, 813, 0, 201], [3141, 639, 0, 168],
    #                [428, 808, 344, 540], [1364, 744, 340, 528], [2268, 744, 320, 532], [3164, 552, 324, 504],
    #                [412, 836, 1012, 552], [1364, 752, 1000, 556], [2268, 736, 1012, 524], [3144, 500, 988, 504]]

    self.average_count_thread = Thread(target=self.average_count_irt)

  def average_count_irt(self):
    # Check queue to see
    image_path_list = []
    self._save_data()

    while True:
      # Wait 2 minutes
      time.sleep(self.thread_sleep_time)

      # Only perform data processing when images are not being taken
      if not self.taking_images.is_set():
        
        self._retrieve_data()
        average_count_dict = dict(zip(self.wavelengths, self.counts))

        new_image_list = []
        print(image_path_list)
        for filename in glob.glob(f"{self.image_folder}/*.png"):
          if not (filename in image_path_list):
            image_path_list.append(filename)
            new_image_list.append(filename)

        if new_image_list == [] and self.is_finished.is_set():
          return

        # Sort images in ascending order of wavelength and time
        """See https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/"""
        new_image_list = sorted(new_image_list, key=lambda string_ : [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)])

        self._process_data(new_image_list, average_count_dict)

  def get_average_count(self):
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
    for filename in image_path_list:
      time = float(filename.split("_")[4])
      if time not in self.times:
        self.times.append(float(filename.split("_")[4]))
      image_array = np.asarray(Image.open(filename))

      if self.blocks == []:
        block_list = np.average(np.array([image_array]))
      else:
        block_list = []
        for block in self.blocks:
          block_list.append(np.average(image_array[block[0]:block[0]+block[1], block[2]:block[2]+block[3]]))

      # Check wavelength of file, if not seen before, add it to the dictionary
      # Creats dictionary of lists of averages of greyscale 
      wavelength = float(filename.split("_")[3])

      if wavelength not in average_count_dict.keys():
        average_count_dict[wavelength] = [block_list]
      else:
        average_count_dict[wavelength].append(block_list)

    self.wavelengths = list(average_count_dict.keys())
    self.counts = list(average_count_dict.values())
    self._save_data()

  def _save_data(self):
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
    
      """
      Storage structure:
      line 1: times separated by commas
      line 2: wavelengths separated by commas
      line 3 onwards: every line is the data collected from each wavelength
                      every chunk separated by '|' represents data collected at each time
                      every element in each chunk is separated by "," represents data collected from a block
      """

  def _retrieve_data(self):
    with open(self.save_file, "r") as file:
      data = file.readlines()
      self.times = [float(time) for time in data[0].split(",")[:-1]]
      self.wavelengths = [float(wavelength) for wavelength in data[1].split(",")[:-1]]
      for count_list in data[2:]:
          self.counts.append([[float(data) for data in count.split(",")[:-1]] for count in count_list.split("|")[:-1]])

    self.counts = [count for count, wavelength in zip(self.counts, self.wavelengths) if wavelength in self.allowed_wavelengths]
    self.wavelengths = [wavelength for wavelength in self.wavelengths if wavelength in self.allowed_wavelengths]
  def plot_data(self):
    n_counts = np.array(self.counts, np.float32)
    normalised_counts = n_counts / n_counts[:, 0][:, np.newaxis]

    if self.blocks == []:
      rows = 1
    else:
      rows = len(self.blocks)

    fig, ax = plt.subplots(rows, 2)
    for i in range(rows):
      if rows < 2:
        coords = ()
      else:
        coords = (i,)
      # Plots power for each wavelength
      ax[coords+(0,)].plot(self.wavelengths, normalised_counts[:,:,i], "x")
      ax[coords + (0,)].legend(np.arange(rows))
      ax[coords+(0,)].set_xlabel("Wavelength (nm)")
      ax[coords+(0,)].set_ylabel("Average Count")

      # Plots power as it changes with time
      # Each row corresponds to each time, hence must transpose array
      ax[coords+(1,)].plot(np.array(self.times) / 60, normalised_counts[:,:,i].T)
      ax[coords+(1,)].legend(np.arange(rows))
      ax[coords+(1,)].set_xlabel("Time (minute)")
      ax[coords+(1,)].set_ylabel("Average Count")

    plt.show()

if __name__ == "__main__":
  processing = AveragePowerOverTimeAndWavelength(image_folder="C:\\Users\\whw29\\Desktop\\Images4", save_file="C:\\Users\\whw29\\Desktop\\RCM\\Image Processing\\average_power_Au3.txt")
  processing._retrieve_data()
  processing.plot_data()
