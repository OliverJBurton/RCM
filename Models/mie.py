from miepython import mie
import numpy as np
import matplotlib.pyplot as plt
from drude import Drude_Gold
from mie_eqns import calc_extinction_coefficient_for_sphere

radius = 10
refractive_index_model = Drude_Gold(radius_nm = 10)

wavelength_range = refractive_index_model.wavelength_in_nm
medium_refractive_index = 1
particle_refractive_index = np.conjugate(refractive_index_model.corrected_refractive_index) # remember convention is negative imaginary part
c_ext = calc_extinction_coefficient_for_sphere(particle_refractive_index, medium_refractive_index, radius*10**(-9), wavelength_range)
# size_parameter = 2*np.pi*1*radius / wavelength_range
# m = particle_refractive_index/medium_refractive_index

# q_ext, q_sca, q_back, g = mie(m, size_parameter)


plt.plot(wavelength_range, c_ext)
plt.xlabel("Wavelength (nm)")
plt.ylabel("Extinction Coefficient")
plt.show()