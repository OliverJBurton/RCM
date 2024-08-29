from miepython import mie
import numpy as np
import matplotlib.pyplot as plt
from drude import Drude

radius = 10**(-7)
wavelength_range = np.linspace(420, 730, 100)
refractive_index_model = Drude(data_range=(420, 730), is_range_wavelength=True)

medium_refractive_index = 1
particle_refractive_index = refractive_index_model.n - refractive_index_model.k * 1j # remember convention is negative imaginary part
size_parameter = 2*np.pi*1*radius / wavelength_range
m = particle_refractive_index/medium_refractive_index

q_ext, q_sca, q_back, g = mie(m, size_parameter)


plt.plot(wavelength_range, q_back)
plt.xlabel("Wavelength (nm)")
plt.ylabel("Extinction efficiency")
plt.show()