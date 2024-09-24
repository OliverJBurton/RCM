import glob
from PIL import Image
import numpy as np
import re
import matplotlib.pyplot as plt
sys.path.append("RCM/Normalise Intensity Experiments/")
from GreyScalePowerExperiment import GreyScalePowerExperiment
from PixelPowerExperiment import PixelPowerExperiment

"""
Assumes all images have the png extension
Assumes image name follows this convention: 'image_cap_' + {index} + '_' + {wavelength} + '_' + {time} + '_img.png'

Assumes GreyScalePowerExperiment and PixelPowerExperiment have been executed and there exists a file with the data inside
"""

class AveragePowerOverTimeAndWavelength:

  def __init__(self, image_folder, processed_image_folder):
    self.image_folder = image_folder
    self.processed_image_folder = processed_image_folder
    self.greyscale_power_table, a, b = GreyScalePowerExperiment().plot_and_fit_greyscale_power()
    self.f_x_y = PixelPowerExperiment().interpolate_data()
    self.time, self.average_power_dict = self.get_average_power()
  
  def _natural_key(string_):
    """See https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]
  
  def get_average_power(self):
    # Get all image file names
    image_path_list = []
    time = []
    for filename in glob.glob(f"{self.image_folder}/*.png"):
      image_path_list.append(filename)
      time.append(float(filename.split("_")[4]))
    
    # Sort image in ascending order of wavelength and time
    image_path_list = sorted(image_path_list, key=self._natural_key)

    average_power_dict = {}
    for filename in image_path_list:
      whole_array = np.asarray(Image.open(filename))
      cut_array = whole_img[400:800,400:800] # Probably gonna be more complex
      power_array = np.vectorise(self.greyscale_power_table.get)(cut_array / self.f_x_y[400:800, 400:800])

      # Check wavelength of file, if not seen before, add it to the dictionary
      # Creats dictionary of lists of averages of greyscale 
      wavelength = int(filename.split("_")[3])
      if wavelength not in time_average_dict.keys():
        average_power_dict[wavelength] = [power_array / power_array.size]
      else:
        average_power_dict[wavelength].append(power_array / power_array.size)

    return time, average_power_dict
  
  def plot_data(self):
    fig, ax = plt.subplot(2, 1)

    # Plots power for each wavelength
    ax[0].plot(self.average_power_dict.keys(), np.array(self.average_power_dict.items()), "rx")
    ax[0].set_xlabel("Wavelength (nm)")
    ax[0].set_ylabel("Average Power (W)")

    # Plots power as it changes with time
    # Each row corresponds to each time, hence must transpose array
    ax[1].plot(np.array(self.time) / 60, np.array(self.average_power_dict.items()).T)
    ax[1].legend()
    ax[1].set_xlabel("Time (minute)")
    ax[1].set_ylabel("Average Power (W)")

    plt.show()



