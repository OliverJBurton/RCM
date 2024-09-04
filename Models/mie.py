from miepython import mie
import numpy as np
import matplotlib.pyplot as plt
from drude import Drude_Gold
from mie_eqns import calc_extinction_coefficient_for_sphere

radius = 40*10**(-9)
refractive_index_model = Drude_Gold()

wavelength_range = refractive_index_model.wavelength_in_nm
new_wavelength_range = np.linspace(wavelength_range[0], wavelength_range[-1], 300)
medium_refractive_index = np.sqrt(2.25)
refractive_index = refractive_index_model.corrected_refractive_index_function_wavelength(new_wavelength_range)
particle_refractive_index = refractive_index.real - 1j*refractive_index.imag # remember convention is negative imaginary part
complex_refractive_index = particle_refractive_index/medium_refractive_index
size_parameter = 2*np.pi*radius*medium_refractive_index/new_wavelength_range
#qext, qsca, qback, g = mie(complex_refractive_index, size_parameter)
c_ext = calc_extinction_coefficient_for_sphere(particle_refractive_index, medium_refractive_index, radius, new_wavelength_range/10**9)
# size_parameter = 2*np.pi*1*radius / wavelength_range
# m = particle_refractive_index/medium_refractive_index

# q_ext, q_sca, q_back, g = mie(m, size_parameter)


plt.plot(new_wavelength_range, c_ext)
plt.xlabel("Wavelength (nm)")
plt.ylabel("Extinction Cross-Section")
plt.xlim((450, 700))
plt.show()