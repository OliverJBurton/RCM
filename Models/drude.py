import matplotlib.pyplot as plt
import numpy as np

# -*- coding: utf-8 -*-

"""
To-do list
- Determine bound electron component
    - https://link.aps.org/accepted/10.1103/PhysRevB.86.235147
"""

class Drude_Gold():
  # Default values are for gold
  def __init__(self, radius_nm=-1, verbose=False):
    # Constants
    self.pi = np.pi
    self.h = 6.62607015 * 10**(-34) / (2*self.pi)
    self.c = 3 * 10**(8)
    self.e = 1.6 * 10**(-19)
    self.v_fermi = 14.1*10**(14) #in nm/s

    # Gold Electronic Properties
    self.gamma_bulk = 1.64 * 10**(14)
    self.plasma_frequency = 1.3 * 10**(16)
    
    # Data taken from https://journals.aps.org/prb/pdf/10.1103/PhysRevB.6.4370
    self.photon_energy_ev = np.array([0.64,0.77,0.89,1.02,1.14,1.26,1.39,1.51,1.64,1.76,1.88,2.01,2.13,2.26,2.38,2.50,2.63,2.75,2.88,3.00,3.12,3.25,3.37,3.50,3.62,3.74,3.87,3.99,4.12,4.24,4.36,4.49,4.61,4.74,4.86,4.98,5.11,5.23,5.36,5.48,5.60,5.73,5.85,5.98,6.10,6.22,6.35,6.47,6.60], np.float32)
    self.n = np.array([0.92,0.56,0.43,0.35,0.27,0.22,0.17,0.16,0.14,0.13,0.14,0.21,0.29,0.43,0.62,1.04,1.31,1.38,1.45,1.46,1.47,1.46,1.48,1.50,1.48,1.48,1.54,1.53,1.53,1.49,1.47,1.43,1.38,1.35,1.33,1.33,1.32,1.32,1.30,1.31,1.30,1.30,1.30,1.30,1.33,1.33,1.34,1.32,1.28])
    self.k = np.array([13.78,11.21,9.519,8.145,7.150,6.350,5.663,5.083,4.542,4.103,3.697,3.272,2.863,2.455,2.081,1.833,1.849,1.914,1.948,1.958,1.952,1.933,1.895,1.866,1.871,1.883,1.898,1.893,1.889,1.878,1.869,1.847,1.803,1.749,1.688,1.631,1.577,1.536,1.497,1.460,1.427,1.387,1.350,1.304,1.277,1.251,1.226,1.203,1.188])

    self.wavelength_in_nm = self.wavelength_in_nm_to_photon_energy_ev(self.photon_energy_ev)
    self.frequency_rad = self.photon_energy_ev*self.e/self.h

    if verbose:
      print(f"The model works between {wavelength_in_nm[0]} nm and {wavelength_in_nm[-1]} nm or {photon_energy_ev[0]} eV and {photon_energy_ev[-1]} eV.")

    # Model parameters
    self.radius_nm = radius_nm

    # elif #data_file is available and radius != -1:
    #   parameters, covariance = self.get_c_parameter(dielectric_function_data)
    #   self.c = parameters[0]
    #   self.error = covariance
    # else:
    self.c = 0

    ## Optical constants
    # Calculate dielectric function from refractive index
    self.real_dielectric_function = self.calc_real_dielectric_function_from_n_and_k(self.n, self.k)
    self.imaginary_dielectric_function = self.calc_imaginary_dielectric_function_from_n_and_k(self.n, self.k)
    # Get free component from Drude's model
    self.free_dielectric_function = self.calc_free_dielectric_function(self.frequency_rad)
    # Get bound component by subtracting free component from total
    self.bound_dielectric_function = self.real_dielectric_function + self.imaginary_dielectric_function*1j - self.free_dielectric_function
    # Get size corrected free component
    self.corrected_free_dielectric_function = self.calc_corrected_free_dielectric_function(self.frequency_rad, self.c)
    # Get size corrected dielectric function
    self.corrected_dielectric_function = self.corrected_free_dielectric_function + self.bound_dielectric_function
    # Get size corrected refractive index
    self.corrected_refractive_index = self.calc_refractive_index(self.corrected_dielectric_function)
  
  def photon_energy_ev_to_wavelength_in_nm(self, photon_energy_ev):
    return self.c / (photon_energy_ev/self.h*self.e/(2*self.pi))* 10**(9)

  def wavelength_in_nm_to_photon_energy_ev(self, wavelength_in_nm):
    return self.c / (wavelength_in_nm/10**9)*2*self.pi/self.e*self.h

  def calc_free_dielectric_function(self, frequency_rad):
    return 1 - self.plasma_frequency**2 / (frequency_rad**2 + 1j*frequency_rad*self.gamma_bulk)
    #return 1 - self.plasma_frequency**2 / (frequency_rad**2 + self.gamma_bulk**2) + (self.plasma_frequency**2*self.gamma_bulk / (frequency_rad*(frequency_rad**2 + self.gamma_bulk**2)))*1j
  
  def calc_corrected_free_dielectric_function(self, frequency_rad, c):
    return 1 - self.plasma_frequency**2 / (frequency_rad**2 + 1j*frequency_rad*(self.gamma_bulk + c*self.v_fermi/self.radius_nm))

  def calc_refractive_index(self, dielectric_function):
    return np.sqrt(np.absolute(dielectric_function)+dielectric_function.real)/4 + np.sqrt(np.absolute(dielectric_function)-dielectric_function.real)/4 * 1j

  def calc_real_dielectric_function_from_n_and_k(self, n, k):
    return n**2 - k**2
  
  def calc_imaginary_dielectric_function_from_n_and_k(self, n, k):
    return 2*n*k

  def get_c_parameter(self, dielectric_function_data):
    parameters, covariance = curve_fit(self.calc_corrected_free_dielectric_function, self.frequency_rad, self.dielectric_function_data)
    return parameters, covariance

  def plot_optical_constants(self, x_limits=(), y_limits=(-7, 7), use_wavelength=False):
    ## Plotting
    fig, ax = plt.subplots(2, 1, sharex=True)

    if use_wavelength:
      x_axis = self.wavelength_in_nm
    else:
      x_axis = self.photon_energy_ev
    
    if x_limits == ():
      x_lim = (x_axis[-1], x_axis[0])
    else:
      x_lim = x_limits

    # Plot for dielectric function
    ax[0].plot(x_axis, self.corrected_dielectric_function.real, label=r"$\epsilon$''")
    ax[0].plot(x_axis, self.corrected_dielectric_function.imag, label=r"$\epsilon$'")
    ax[0].plot(self.plasma_frequency*self.h/self.e, 0, "rx")
    ax[0].axhline(0, color="black", lw=1)
    ax[0].set_ylabel("$\epsilon$")
    #ax[0].set_ylim((-8, 8))
    ax[0].legend()
    ax[0].minorticks_on()

    # Plot for refractive indices
    ax[1].plot(x_axis, self.corrected_refractive_index.real, label="n")
    ax[1].plot(x_axis, self.corrected_refractive_index.imag, label="k")
    ax[1].legend()
    ax[1].set_ylabel("Refractive index")

    if use_wavelength:
      ax[1].set_xlabel("Wavelength (nm)")
    else:
      ax[1].set_xlabel("Photon energy (ev)")

    ax[0].set_xlim(x_lim)
    ax[1].set_xlim(x_lim)
    ax[0].set_ylim(y_limits)
    ax[1].set_ylim(0, y_limits[1])

    # Set up secondary x-axis
    # if use_wavelength:
    #   secax = ax[0].secondary_xaxis("top", functions=(self.wavelength_in_nm_to_photon_energy_ev, self.photon_energy_ev_to_wavelength_in_nm))
    # else:
    #   secax = ax[0].secondary_xaxis("top", functions=(self.photon_energy_ev_to_wavelength_in_nm, self.wavelength_in_nm_to_photon_energy_ev))
    # secax.set_xlabel("Wavelength (nm)")
    # secax.tick_params(axis="x", rotation=45)
    # secax.minorticks_on()

    plt.show()

if __name__ == "__main__":
  # wavelength_range = np.linspace(200, 1000, 100)
  # photon_energy_ev = np.linspace(1, 6, 100)
  model = Drude_Gold(radius_nm=1)
  model.plot_optical_constants(x_limits=(200, 1000), y_limits=(-50, 5), use_wavelength=True)
