import ExperimentGUI
from threading import Thread
import numpy as np
import matplotlib.pyplot as plt
import time

class GreyScalePowerExperiment(ExperimentGUI.ExperimentGUI):
  '''
  Determine the relationship between power of light on the sample with respect to the greyscale of the image taken by the camera

  :param step: the interval between greyscale values wherein measurements are taken
  '''

  def __init__(self, file_name="greyscale_power_readings.txt", current_mA=100, do_plot=True, use_stored_data=False):
    super().__init__(file_name=file_name, greyscale=0, current_mA=current_mA, do_plot=do_plot, use_stored_data=use_stored_data)

    # Greyscale power experiment parameters
    self.greyscale_power_readings = []

    if not use_stored_data:

      # Creates a daemon thread for the greyscale power experiment to run in the background
      self.greyscale_power_experiment_thread = Thread(target=self.greyscale_power_experiment, daemon=True)

      self.after(self.refresh_rate_ms, self.call_handler)
    else:
      self.end_experiment()

  def set_greyscale(self, greyscale):
    '''
    Sets the luminance of the greyscale background image
    '''
    self.canvas.config(bg=f"#{greyscale:02X}{greyscale:02X}{greyscale:02X}")

  def greyscale_power_experiment(self):
    '''
    Runs experiment to obtain relationship between greyscale of the image projected and the light power at the end of the microscope
    Writes data to file called greyscale_power_readings.txt (by default)
    '''

    print("Begin Experiment")

    # Full screen and wait until full screen process is finished
    self.make_call(self.activate_full_screen)
    time.sleep(1)

    # Loops through the greyscale range starting from white
    for i in range(0, 256, 1):
      # Request main thread to update the greyscale
      self.make_call(self.set_greyscale, i)
      # Take readings
      self.greyscale_power_readings.append([i, float(self.power_meter.get_power_reading_W_str())])

    # Write to file
    with open(self.file_name, "w") as file:
      file.write(f"{self.greyscale_power_readings[0][1]}\n")
      for reading in self.greyscale_power_readings:
        file.write(f"{reading[0]},{reading[1]}\n")

    # Requests main thread to end experiment
    print("End Experiment")
    self.make_call(self.destroy)

  def plot_and_fit_greyscale_power(self):
    '''
    Plots and fits a polynomial to the light power against the greyscale. Data taken from textfile or from self.greyscale_power_readings

    :param fileName: name of textfile storing the data.
    :param order: order of the polynomial fitted
    '''
    data = super()._get_file_data(readings=self.greyscale_power_readings)

    greyscale, power_proportion = data[:, 0], (data[:, 1] - self.background_power) / np.max(data[:, 1])
    for i, element in enumerate(power_proportion):
      if power_proportion[i] < 0 and element != power_proportion[-1]:
        power_proportion[i] = (power_proportion[i-1] + power_proportion[i+1]) / 2

    scaled_data = np.stack((greyscale, power_proportion), axis=1)
    greyscale_power_table = dict(scaled_data)

    sorted_data = scaled_data[scaled_data[:,1].argsort()]
    
    def power_greyscale_table(sorted_data, value):
      """
      Bisection function
      """
      idx = np.searchsorted(sorted_data[:,1], value, side="left")
      idx = np.where(np.logical_and(idx > 0, idx == len(sorted_data[:,1])), idx-1, idx)
      idx = np.where(np.abs(value - sorted_data[idx-1,1]) < np.abs(value - sorted_data[idx,1]), idx-1, idx)
      return sorted_data[idx,0]

    if self.do_plot:
      # Plot of greyscale (x-axis) vs G (y-axis)
      fig, ax = plt.subplots(2, 1)
      ax[0].plot(greyscale, power_proportion)
      ax[0].set_xlim(greyscale[0], greyscale[-1])
      ax[0].set_ylim(bottom=np.min(power_proportion))
      ax[0].set_xlabel("Greyscale")
      ax[0].set_ylabel("G")

      # Plot of G (x-axis) vs greyscale (y-axis)
      ax[1].plot(power_proportion, greyscale)
      ax[1].set_xlim(np.min(power_proportion), np.max(power_proportion))
      ax[1].set_ylim(np.min(greyscale), np.max(greyscale))
      ax[1].set_xlabel("G")
      ax[1].set_ylabel("Greyscale")

      plt.show()

    return greyscale_power_table, power_greyscale_table, sorted_data

if __name__ == "__main__":
  screen = GreyScalePowerExperiment()
  screen.plot_and_fit_greyscale_power()