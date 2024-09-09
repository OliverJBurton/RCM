import numpy as np

photon_energy_ev = np.array([0.64,0.77,0.89,1.02,1.14,1.26,1.39,1.51,1.64,1.76,1.88,2.01,2.13,2.26,2.38,2.50,2.63,2.75,2.88,3.00,3.12,3.25,3.37,3.50,3.62,3.74,3.87,3.99,4.12,4.24,4.36,4.49,4.61,4.74,4.86,4.98,5.11,5.23,5.36,5.48,5.60,5.73,5.85,5.98,6.10,6.22,6.35,6.47,6.60])
n = np.array([1.09,0.76,0.60,0.48,0.36,0.32,0.30,0.26,0.24,0.21,0.22,0.30,0.70,1.02,1.18,1.22,1.25,1.24,1.25,1.28,1.32,1.33,1.36,1.37,1.36,1.34,1.38,1.38,1.40,1.42,1.45,1.46,1.45,1.41,1.41,1.37,1.34,1.28,1.23,1.18,1.13,1.08,1.04,1.01,0.99,0.98,1.97,0.95,1.94])
k = np.array([0.24,0.15,0.13,0.09,0.04,0.04,0.04,0.04,0.03,0.04,0.05,0.06,0.05,0.06,0.05,0.05,0.05,0.04,0.04,0.05,0.05,0.05,0.07,0.10,0.14,0.17,0.81,1.13,1.34,1.39,1.41,1.41,1.38,1.35,1.33,1.31,1.30,1.28,1.28,1.26,1.25,1.22,1.20,1.18,1.15,1.14,1.12,1.10,1.07])
print(len(photon_energy_ev))

with open("./Models/model_data/.txt", "a") as file:
  for item in photon_energy_ev:
    file.write(f"{item},")
  file.write("\n")

# 14.0e15
# 4.6e13