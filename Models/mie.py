from miepython import mie
import numpy as np
import matplotlib.pyplot as plt
from drude import Drude_Gold
from mie_eqns import calc_extinction_coefficient_for_sphere

radius = 40*10**(-9)
refractive_index_model = Drude_Gold()

wavelength_range = refractive_index_model.wavelength_in_nm
medium_refractive_index = np.sqrt(2.25)
particle_refractive_index = refractive_index_model.n - 1j*refractive_index_model.k # remember convention is negative imaginary part
complex_refractive_index = particle_refractive_index/medium_refractive_index
size_parameter = 2*np.pi*radius*medium_refractive_index/wavelength_range
#qext, qsca, qback, g = mie(complex_refractive_index, size_parameter)
c_ext = calc_extinction_coefficient_for_sphere(particle_refractive_index, medium_refractive_index, radius, wavelength_range/10**9)
# size_parameter = 2*np.pi*1*radius / wavelength_range
# m = particle_refractive_index/medium_refractive_index

# q_ext, q_sca, q_back, g = mie(m, size_parameter)


plt.plot(wavelength_range, c_ext)
plt.xlabel("Wavelength (nm)")
plt.ylabel("Extinction Cross-Section")
plt.xlim((450, 700))
plt.show()