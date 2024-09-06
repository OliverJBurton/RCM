import matplotlib.pyplot as plt
import numpy as np

# -*- coding: utf-8 -*-

"""
Data
- Fermi velocity, plasma frequency, and damping constant of gold
    https://iopscience.iop.org/article/10.1088/0957-4484/16/1/030/pdf
- Fermi velocity, plasma frequency, and damping constant of silver and copper
    https://www.researchgate.net/figure/Lorentz-Drude-model-parameters-for-gold_tbl1_260291014
    http://230nsc1.phy-astr.gsu.edu/hbase/Tables/fermi.html
- Data for refractive indices of gold, copper, and silver
    https://journals.aps.org/prb/pdf/10.1103/PhysRevB.6.4370
"""

# Note the refractive index and wavelength function are fairly valid up to 900 nm

class Drude():
  '''
  Drude model for modelling the dielectric function of pure metals
  Includes size correction for when radius of the particle is less than free path length and additional damping arises due to electron collision with boundary
  Works for frequencies corresponding to photon energies of 0.64 eV - 6.6 eV (or 200 nm to 1800 nm)
  Uses data from Johnson and Christy 

  :param radius_nm: radius or characteristic length of the particle
  :param metal: determines which metals to use, supports ("gold", "silver")
  :param order: determines the order of the polynomial to fit the data with
  '''
  def __init__(self, radius_nm=-1, metal="gold",order=7):

    # Constants
    self.pi = np.pi
    self.h = 6.62607015 * 10**(-34) / (2*self.pi)
    self.c = 3 * 10**(8)
    self.e = 1.6 * 10**(-19)

    # Model parameters
    self.radius_nm = radius_nm
    self.order = order

    # Obtain Electronic Properties of the selected metal
    with open(f"C:\\Users\\whw29\\Desktop\\RCM\\Models\\model_data\\{metal}.txt", "r") as file:
      self.gamma_bulk = float(file.readline())
      self.plasma_frequency = float(file.readline())
      self.v_fermi = float(file.readline()) #in nm/s
      self.D = float(file.readline())

      # If radius of particle is not smaller than free path length then deactivate size-corrections
      if radius_nm == -1 or radius_nm > 1/self.gamma_bulk:
        self.D = 0
      
      # Data required to obtain bound electron component which is assumed size independent
      self.photon_energy_ev = np.array(list(file.readline().split(","))[:-1], np.float32)
      self.n = np.array(list(file.readline().split(","))[:-1], np.float32)
      self.k = np.array(list(file.readline().split(","))[:-1], np.float32)
    
    # Used for scale of graph and the parameter of the polynomial fitted functions
    self.wavelength_in_nm = self.wavelength_in_nm_to_photon_energy_ev(self.photon_energy_ev)
    # Used for calculation of free dielectric component
    self.frequency_rad = self.photon_energy_ev*self.e/self.h

    ## Optical constants
    # Calculate dielectric function from refractive index, subtract away the free component to get bound component
    # Calculate size corrected free component then add to size-independent bound component to get size-corrected dielectric functions
    self.dielectric_data = self.calc_dielectric_data_from_refractive_index(self.n + 1j*self.k)
    self.free_dielectric_data = self.calc_free_dielectric_data(self.frequency_rad)
    self.bound_dielectric_data = self.dielectric_data - self.free_dielectric_data
    self.corrected_free_dielectric_data = self.calc_corrected_free_dielectric_data(self.frequency_rad, self.D)
    self.corrected_dielectric_data = self.corrected_free_dielectric_data + self.bound_dielectric_data
    self.corrected_refractive_index = self.calc_refractive_index_from_dielectric_data(self.corrected_dielectric_data)

    # Find dielectric constant and refractive index as analytical functions of wavelength
    self.corrected_free_dielectric_function_wavelength = self.get_poly_fit_function(self.corrected_dielectric_data, self.wavelength_in_nm, self.order)
    self.corrected_refractive_index_function_wavelength = self.get_poly_fit_function(self.corrected_refractive_index, self.wavelength_in_nm, self.order)
  
  def photon_energy_ev_to_wavelength_in_nm(self, photon_energy_ev):
    '''
    Converts photon energy (eV) to wavelength (nm)

    :param photon_energy_ev: numpy array of or scalar photon energy in electron volts
    :returns: numpy array of or scalar wavelength in nanometers
    '''
    return self.c / (photon_energy_ev/self.h*self.e/(2*self.pi))* 10**(9)

  def wavelength_in_nm_to_photon_energy_ev(self, wavelength_in_nm):
    '''
    Converts wavelength (nm) to photon energy (eV)

    :param wavelength_in_nm: numpy array of or scalar wavelength in nanometers
    :returns: numpy array of or scalar photon energy in electron volts
    '''
    return self.c / (wavelength_in_nm/10**9)*2*self.pi/self.e*self.h

  def calc_free_dielectric_data(self, frequency_rad):
    '''
    Calculates the free component of the dielectric function without size consideration

    :param frequency_rad: numpy array of or scalar frequency in radians
    :return: numpy array of or scalar free dielectric constant
    '''
    return 1 - self.plasma_frequency**2 / (frequency_rad**2 + 1j*frequency_rad*self.gamma_bulk)
    #return 1 - self.plasma_frequency**2 / (frequency_rad**2 + self.gamma_bulk**2) + (self.plasma_frequency**2*self.gamma_bulk / (frequency_rad*(frequency_rad**2 + self.gamma_bulk**2)))*1j
  
  def calc_corrected_free_dielectric_data(self, frequency_rad, D):
    '''
    Calculates the size corrected free component of the dielectric function

    :param frequency_rad: numpy array of or scalar frequency in radians
    :param D: constant including details of the scattering process (essentially proportionality constant relating radius of particle to the effective mean free path for collisions with boundary)
    :return: numpy array of or scalar size-corrected free dielectric constant
    '''
    return 1 - self.plasma_frequency**2 / (frequency_rad**2 + 1j*frequency_rad*(self.gamma_bulk + D*self.v_fermi/self.radius_nm))

  def calc_refractive_index_from_dielectric_data(self, dielectric_data):
    '''
    Calculates refractive index from dielectric constant
    :param dielectric_data: numpy array of or scalar dielectric constant
    :return: numpy array or scalar refractive index
    '''
    return np.sqrt((np.absolute(dielectric_data)+dielectric_data.real)/2) + np.sqrt((np.absolute(dielectric_data)-dielectric_data.real)/2) * 1j

  def calc_dielectric_data_from_refractive_index(self, N):
    '''
    Calculates dielectric data from the refractive index
    :param N: numpy array of or scalar refractive indesx
    :return: numpy array of or scalar dielectric constant
    '''
    return (N.real**2 - N.imag**2) + 2j*N.real*N.imag

  def get_poly_fit_function(self, y, x, order):
    '''
    Obtain an analytical polynomial function of y as a function of x
    :param y: numpy array of output
    :param x: numpy array of corresponding inputs
    :param order: order of the polynomial
    :return: analytical function 
    '''
    z = np.polyfit(x, y, order)
    return np.poly1d(z)

  def plot_optical_constants(self, x_limits=(), y_limits=(-7, 7), use_wavelength=False):
    '''
    Plots a graph of the real and imaginary value of the dielectric constant and that of the refractive index against photon energy (eV) or wavelength (nm)
    :param x_limits: tuple of lower and upper bound for the photon energy or wavelength
    :param y_limits: tuple of lower and upper bound for the dielectric constant and refractive index
    :use_wavelength: boolean, determines whether x-axis is wavelength or photon energy
    '''
    ## Plotting
    fig, ax = plt.subplots(2, 1, sharex=True)

    # Change x_axis accordingly
    if use_wavelength:
      x_axis = self.wavelength_in_nm
      x_new = np.linspace(x_axis[0], x_axis[-1], 100)
      corrected_free_dielectric_function = self.corrected_free_dielectric_function_wavelength(x_new)
      corrected_refractive_index_function = self.corrected_refractive_index_function_wavelength(x_new)
    else:
      x_axis = self.photon_energy_ev
      x_new = np.linspace(x_axis[0], x_axis[-1], 100)
      corrected_free_dielectric_function = self.get_poly_fit_function(self.corrected_dielectric_data, self.photon_energy_ev, self.order)(x_new)
      corrected_refractive_index_function = self.get_poly_fit_function(self.corrected_refractive_index, self.photon_energy_ev, self.order)(x_new)

    # Set custom limit if provided
    if x_limits == ():
      x_lim = (x_axis[-1], x_axis[0])
    else:
      x_lim = x_limits

    # Plot for dielectric function
    ax[0].plot(x_axis, self.corrected_dielectric_data.real, 'rx', x_new, corrected_free_dielectric_function.real, label=r"$\epsilon$''")
    ax[0].plot(x_axis, self.corrected_dielectric_data.imag, 'bx', x_new, corrected_free_dielectric_function.imag, label=r"$\epsilon$''")
    ax[0].plot(self.plasma_frequency*self.h/self.e, 0, "rx")
    ax[0].axhline(0, color="black", lw=1)
    ax[0].set_ylabel("$\epsilon$")
    ax[0].legend()
    ax[0].minorticks_on()

    # Plot for refractive indices
    # ax[1].plot(x_axis, self.n, label="n")
    # ax[1].plot(x_axis, self.k, label="k")
    ax[1].plot(x_axis, self.corrected_refractive_index.real, 'rx', x_new, corrected_refractive_index_function.real, label="n")
    ax[1].plot(x_axis, self.corrected_refractive_index.imag, 'bx', x_new, corrected_refractive_index_function.imag, label="k")
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
    if use_wavelength:
      secax = ax[0].secondary_xaxis("top", functions=(self.wavelength_in_nm_to_photon_energy_ev, self.photon_energy_ev_to_wavelength_in_nm))
      secax.set_xlabel("Photon Energy (ev)")
    else:
      secax = ax[0].secondary_xaxis("top", functions=(self.photon_energy_ev_to_wavelength_in_nm, self.wavelength_in_nm_to_photon_energy_ev))
      secax.set_xlabel("Wavelength (nm)")
      secax.tick_params(axis="x", rotation=45)
    secax.minorticks_on()

    plt.show()

if __name__ == "__main__":
  # wavelength_range = np.linspace(200, 1000, 100)
  # photon_energy_ev = np.linspace(1, 6, 100)
  model = Drude(radius_nm=1, metal="silver")
  model.plot_optical_constants(y_limits=(-50, 10), use_wavelength=True)
