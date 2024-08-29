import matplotlib.pyplot as plt
import numpy as np

# -*- coding: utf-8 -*-

"""
To-do list
- Determine bound electron component
    - Either from: https://link.aps.org/accepted/10.1103/PhysRevB.86.235147 or mangadex.org/title/829fc3a7-d4f4-42e9-9032-0917083f9e0d/nan-hao-shang-feng
"""

class Drude():
  def __init__(self, plasma_frequency=1.3 * 10**(16), gamma_bulk=1.64 * 10**(14), data_range=(6, 20), is_range_wavelength=False, no_data_points=100):
    # Constants
    self.pi = np.pi
    self.h = 6.62607015 * 10**(-34) / (2*self.pi)
    self.c = 3 * 10**(8)
    self.e = 1.6 * 10**(-19)

    # Model parameters
    self.plasma_frequency = plasma_frequency
    self.gamma_bulk = gamma_bulk
    self.no_data_points = no_data_points

    if is_range_wavelength == True:
      self.wavelength_in_nm = np.linspace(data_range[0], data_range[1], no_data_points)
      self.photon_energy_ev = self.wavelength_in_nm_to_photon_energy_ev(self.wavelength_in_nm)
    else:
      self.photon_energy_ev = np.linspace(data_range[0], data_range[1], no_data_points)
      self.wavelength_in_nm = self.photon_energy_ev_to_wavelength_in_nm(self.photon_energy_ev)
    self.frequency_rad = self.photon_energy_ev*self.e/self.h

    # Optical constants
    self.real_dielectric_function = self.calc_real_dielectric_function()
    self.imaginary_dielectric_function = self.calc_imaginary_dielectric_function()
    self.n = self.calc_n()
    self.k = self.calc_k()

  def photon_energy_ev_to_wavelength_in_nm(self, photon_energy_ev):
    return self.c / (photon_energy_ev*self.e/self.h/(2*self.pi))* 10**(9)

  def wavelength_in_nm_to_photon_energy_ev(self, wavelength_in_nm):
    return self.c / (wavelength_in_nm/10**9)*2*self.pi*self.h/self.e
  
  def calc_real_dielectric_function(self):
    return 1 - self.plasma_frequency**2 / (self.frequency_rad**2 + self.gamma_bulk**2)
  
  def calc_imaginary_dielectric_function(self):
    return self.plasma_frequency**2*self.gamma_bulk / (self.frequency_rad*(self.frequency_rad**2 + self.gamma_bulk**2))
  
  def calc_n(self):
    return np.sqrt(np.sqrt(self.real_dielectric_function**2 + self.imaginary_dielectric_function**2)+self.real_dielectric_function)/4
  
  def calc_k(self):
    return np.sqrt(np.sqrt(self.real_dielectric_function**2 + self.imaginary_dielectric_function**2)-self.real_dielectric_function)/4

  def plot_optical_constants(self):
    ## Plotting
    fig, ax = plt.subplots(2, 1, sharex=True)

    # Plot for dielectric function
    ax[0].plot(self.photon_energy_ev, self.imaginary_dielectric_function, label=r"$\epsilon$''")
    ax[0].plot(self.photon_energy_ev, self.real_dielectric_function, label=r"$\epsilon$'")
    ax[0].plot(self.plasma_frequency*self.h/self.e, 0, "rx")
    ax[0].axhline(0, color="black", lw=1)
    ax[0].set_ylabel("$\epsilon$")
    #ax[0].set_ylim((-8, 8))
    ax[0].legend()
    ax[0].minorticks_on()
    ax[0].set_xlim((self.photon_energy_ev[0], self.photon_energy_ev[-1]))

    # Plot for refractive indices
    ax[1].plot(self.photon_energy_ev, self.n, label="n")
    ax[1].plot(self.photon_energy_ev, self.k, label="k")
    ax[1].legend()
    ax[1].set_ylabel("Refractive index")
    ax[1].set_xlabel("Photon energy (ev)")
    ax[1].set_xlim((self.photon_energy_ev[0], self.photon_energy_ev[-1]))

    # Set up secondary x-axis
    secax = ax[0].secondary_xaxis("top", functions=(self.photon_energy_ev_to_wavelength_in_nm, self.wavelength_in_nm_to_photon_energy_ev))
    secax.set_xlabel("Wavelength (nm)")
    secax.tick_params(axis="x", rotation=45)
    secax.minorticks_on()

    plt.show()

if __name__ == "__main__":
  refractive_index_model = Drude(data_range=(420, 730), is_range_wavelength=True)
  refractive_index_model.plot_optical_constants()