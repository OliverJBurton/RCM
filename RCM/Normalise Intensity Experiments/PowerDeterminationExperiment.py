from PixelPowerExperiment import PixelPowerExperiment
from GreyScalePowerExperiment import GreyScalePowerExperiment
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from DebugScreen import DebugScreen

class LightIntensityDetermination:
  """
  Performs the greyscale power and pixel power experiment to determine the required greyscale to project the desired light intensity on a point on the sample

  :param kernel_dim: size of the kernels used in the pixel power experiment
  :param do_plot: plot figures of the result of both experiments
  """
  def __init__(self, image_path="", kernel_dim=(60,60), do_plot=True, use_stored_data=False):
    """
    Rescaling equation
    E_xy: power of pixel at position (x, y)
    E_max_xy: maximum power of pixel at position (x, y)
    B_xy: background power of pixel at position (x, y)
    min_E_max: smallest maximum power of all the pixels (pixel with this power is the limiting pixel)
    min_B: background power of the limiting pixel

    corrected_E - min_B = (E_xy - B_xy) / (E_max_xy - B_xy) * (min_E_max - min_B)
    
    """

    # Obtain relationship between greyscale and light power
    experiment1 = GreyScalePowerExperiment(do_plot=do_plot)
    if not use_stored_data:
      experiment1.greyscale_power_experiment_thread.start()
      experiment1.mainloop()
    else:
      experiment1.end_experiment()

    self.greyscale_power_table, self.power_greyscale_table, sorted_data = experiment1.plot_and_fit_greyscale_power()

    # Obtain f(x, y): 
    experiment2 = PixelPowerExperiment(kernel_dim=kernel_dim, do_plot=do_plot)
    if not use_stored_data:
      experiment2.pixel_power_experiment_thread.start()
      experiment2.mainloop()
    else:
      experiment2.end_experiment()

    self.f_x_y = experiment2.interpolate_data() # Also is max power array
    self.exp_screen_res = experiment2.exp_screen_res

    # Open image in greyscale mode, scale it to resolution of projector screen
    # Possible error could arise if image as a transparency channel
    # image_array = np.asarray(Image.open(image_path).convert("L"), dtype=np.uint8)
    # np.set_printoptions(threshold=np.inf)
    greyscale_array = self.open_scale_image(image_path)

    # Get range of powers, scale power to be within range
    max_min_power = np.min(self.f_x_y[:,120:-60])
    print(max_min_power)
    print(self.greyscale_power_table)
    power_array = np.vectorize(self.greyscale_power_table.get)(greyscale_array) * max_min_power
    plt.contourf(power_array, levels=30, cmap="RdGy")
    plt.colorbar()
    plt.show()
    scaled_G_array = power_array / (self.f_x_y)
    print(np.max(scaled_G_array))
    plt.contourf(scaled_G_array, levels=30, cmap="RdGy")
    plt.colorbar()
    plt.show()
    corrected_greyscale_array = self.power_greyscale_table(sorted_data, scaled_G_array)
    plt.contourf(corrected_greyscale_array, levels=200, cmap="RdGy")
    plt.colorbar()
    plt.show()

    corrected_rgb_array = np.repeat(corrected_greyscale_array.reshape(self.exp_screen_res[::-1] + (1,)), 3, axis=2)
    corrected_image = Image.fromarray(corrected_rgb_array.astype(np.uint8), "RGB")
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


if __name__ == "__main__":
  # screen = DebugScreen(greyscale=0, current_mA=100)

  # screen = GreyScalePowerExperiment()
  # screen.greyscale_power_experiment_thread.start()
  # screen.mainloop()
  # screen.plot_and_fit_greyscale_power()

  # experiment = PixelPowerExperiment(image_path="C:\\Users\\whw29\\Desktop\\test.png", file_name="pixel_power_test.txt", kernel_dim=(60, 60))
  # experiment.pixel_power_experiment_thread.start()
  # experiment.mainloop()
  # experiment.interpolate_data()

  # screen = LightIntensityDetermination()

  experiment = PixelPowerExperiment(image_path="C:\\Users\\whw29\\Desktop\\test.png", file_name="pixel_power_test.txt")
  experiment.pixel_power_experiment_thread.start()
  experiment.mainloop()
  experiment.interpolate_data()
  screen = LightIntensityDetermination(image_path="C:\\Users\\whw29\\Desktop\\test.png", do_plot=True, use_stored_data=True)
  experiment = PixelPowerExperiment(image_path="C:\\Users\\whw29\\Desktop\\test_corrected.png", file_name="pixel_power_test.txt")
  experiment.pixel_power_experiment_thread.start()
  experiment.mainloop()
  experiment.interpolate_data()