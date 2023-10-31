# First, we import the matplotlib library, which is useful for creating static, animated, and interactive visualizations in Python.
import matplotlib.pyplot as plt

# Importing the Thorlabs device library from the pylablib, which is a Python library for control and data acquisition in scientific experiments.
from pylablib.devices import Thorlabs as tl
import pylablib as pll

pll.par["devices/dlls/thorlabs_tlcam"] = r"C:\Program Files\Thorlabs\Scientific Imaging\ThorCam"

# NumPy is a Python library used for working with arrays. It also has functions for working in domain of linear algebra, Fourier transform, and matrices.
import numpy as np

print(tl.list_cameras_tlcam())
cam1 = tl.ThorlabsTLCamera(serial="24070")
cam1.set_exposure(10E-3)
images = cam1.grab(1)
cam1.close()