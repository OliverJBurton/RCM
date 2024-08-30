import numpy as np
from numba import njit, int32, float64, complex128
from scipy.special import riccati_jn, riccati_yn

@njit((complex128, int32), cache=True)
def _Lentz_Dn(z, N):
  """
  Compute the logarithmic derivative of the Ricatti-Bessel function.

  Args:
      z: function argument
      N: order of Ricatti-Bessel function

  Returns:
      This returns the Ricatti-Bessel function of order N with argument z
      using the continued fraction technique of Lentz, Appl. Opt., 15,
      668-671, (1976).
  """
  zinv = 2.0 / z
  alpha = (N + 0.5) * zinv
  aj = -(N + 1.5) * zinv
  alpha_j1 = aj + 1 / alpha
  alpha_j2 = aj
  ratio = alpha_j1 / alpha_j2
  runratio = alpha * ratio

  while np.abs(np.abs(ratio) - 1.0) > 1e-12:
    aj = zinv - aj
    alpha_j1 = 1.0 / alpha_j1 + aj
    alpha_j2 = 1.0 / alpha_j2 + aj
    ratio = alpha_j1/alpha_j2
    zinv *= -1
    runratio = ratio * runratio
  
  return -N/z + runratio

@njit((complex128, int32, complex128[:]), cache=True)
def _D_downwards(z, N, D):
  """
  Compute the logarithmic derivative by downwards recurrence.

  Args:
      z: function argument
      N: order of Ricatti-Bessel function
      D: gets filled with the Ricatti-Bessel function values for orders
          from 0 to N for an argument z using the downwards recurrence relations.
  """
  last_D = _Lentz_Dn(z, N)
  for n in range(N, 0, -1):
    last_D = n / z - 1.0 / (last_D + n / z)
    D[n - 1] = last_D

@njit((complex128, int32, complex128[:]), cache=True)
def _D_upwards(z, N, D):
    """
    Compute the logarithmic derivative by upwards recurrence.

    Args:
        z: function argument
        N: order of Ricatti-Bessel function
        D: gets filled with the Ricatti-Bessel function values for orders
           from 0 to N for an argument z using the upwards recurrence relations.
    """
    exp = np.exp(-2j * z)
    D[1] = -1 / z + (1 - exp) / ((1 - exp) / z - 1j * (1 + exp))
    for n in range(2, N):
        D[n] = 1 / (n / z - D[n - 1]) - n / z

@njit((complex128, float64, int32), cache=True)
def _D_calc(m, x, N):
  """
  Compute the logarithmic derivative using best method.

  Args:
      m: the complex index of refraction of the sphere
      x: the size parameter of the sphere
      N: order of Ricatti-Bessel function

  Returns:
      The values of the Ricatti-Bessel function for orders from 0 to N.
  """
  n = m.real
  kappa = np.abs(m.imag)
  D = np.zeros(N, dtype=np.complex128)

  if n < 1 or n > 10 or kappa > 10 or x * kappa >= 3.9 - 10.8 * n + 13.78 * n**2:
    _D_downwards(m * x, N, D)
  else:
    _D_upwards(m * x, N, D)
  return D

@njit((complex128, float64), cache=True)
def _mie_An_Bn(m, x):
  """
  Compute arrays of Mie coefficients A and B for a sphere.

  This estimates the size of the arrays based on Wiscombe's formula. The length
  of the arrays is chosen so that the error when the series are summed is
  around 1e-6.

  Args:
      m: the complex index of refraction of the sphere
      x: the size parameter of the sphere

  Returns:
      a, b: arrays of Mie coefficents An and Bn
  """
  nstop = int(x + 4.05 * x**0.33333 + 2.0) + 1
  a = np.zeros(nstop - 1, dtype=np.complex128)
  b = np.zeros(nstop - 1, dtype=np.complex128)

  psi_nm1 = np.sin(x)                   # nm1 = n-1 = 0
  psi_n = psi_nm1 / x - np.cos(x)       # n = 1
  xi_nm1 = complex(psi_nm1, np.cos(x))
  xi_n = complex(psi_n, np.cos(x) / x + np.sin(x))

  if m.real > 0.0:
      D = _D_calc(m, x, nstop + 1)

      for n in range(1, nstop):
          temp = D[n] / m + n / x
          a[n - 1] = (temp * psi_n - psi_nm1) / (temp * xi_n - xi_nm1)
          temp = D[n] * m + n / x
          b[n - 1] = (temp * psi_n - psi_nm1) / (temp * xi_n - xi_nm1)
          xi = (2 * n + 1) * xi_n / x - xi_nm1
          xi_nm1 = xi_n
          xi_n = xi
          psi_nm1 = psi_n
          psi_n = xi_n.real
  else:
      for n in range(1, nstop):
          a[n - 1] = (n * psi_n / x - psi_nm1) / (n * xi_n / x - xi_nm1)
          b[n - 1] = psi_n / xi_n
          xi = (2 * n + 1) * xi_n / x - xi_nm1
          xi_nm1 = xi_n
          xi_n = xi
          psi_nm1 = psi_n
          psi_n = xi_n.real

  return a, b

#@njit((complex128, complex128, float64, float64), cache=True)
def _mie_An_Bn_coated(m_1, m_2, x, y):
  # Remember to make the imaginary part of m1 and m2 positive
  nstop = int(x + 4.05 * x**0.33333 + 2.0) + 1
  a = np.zeros(nstop - 1, dtype=np.complex128)
  b = np.zeros(nstop - 1, dtype=np.complex128)
  A = np.zeros(nstop - 1, dtype=np.complex128)
  B = np.zeros(nstop - 1, dtype=np.complex128)

  # Calculation of A and B
  psi_n_m1x, dpsi_n_m1x = riccati_jn(nstop-1, m_1*x)
  psi_n_m2x, dpsi_n_m2x = riccati_jn(nstop-1, m_2*x)

  chi_n_m2x, dchi_n_m2x = riccati_yn(nstop-1, m_2*x)

  A = (m_2*psi_n_m2x*dpsi_n_m1x - m_1*dpsi_n_m2x*psi_n_m1x) / (m_2*chi_n_m2x*dpsi_n_m1x - m_1*dchi_n_m2x*psi_n_m1x)
  B = (m_2*psi_n_m1x*dpsi_n_m2x - m_1*psi_n_m2x*dpsi_n_m1x) / (m_2*dchi_n_m2x*psi_n_m1x - m_1*dpsi_n_m1x*chi_n_m2x)
  
  # Calculation of a and b
  psi_n_y, dpsi_n_y = riccati_jn(nstop-1, y)
  psi_n_m2y, dpsi_n_m2y = riccati_jn(nstop-1, m_2*y)

  chi_n_y, dchi_n_y = riccati_yn(nstop-1, x)
  chi_n_m2y, dchi_n_m2y = riccati_yn(nstop-1, m_2*y)

  eta_n_y, deta_n_y = np.add((-chi_n_y*1j, -dchi_n_y*1j), (psi_n_y, dpsi_n_y))

  a = (psi_n_y*(dpsi_n_m2y - A*dchi_n_m2y) - m_2*dpsi_n_y*(psi_n_m2y - A*chi_n_m2y)) / (eta_n_y*(dpsi_n_m2y - A*dchi_n_m2y) - m_2*eta_n_y*(psi_n_m2y - A*chi_n_m2y))
  b = (m_2*psi_n_y*(dpsi_n_m2y - B*dchi_n_m2y) - dpsi_n_y*(psi_n_m2y - B*chi_n_m2y)) / (m2*eta_n_y*(dpsi_n_m2y - B*dchi_n_m2y) - deta_n_y*(psi_n_m2y - B*chi_n_m2y))

  return a,b

@njit((complex128, float64), cache=True)
def _calc_extinction_efficiency_scalar(m, x):
  a, b = _mie_An_Bn(m, x)
  n = np.arange(1, len(a)+1)

  Q_ext = 2*np.sum((2.0*n + 1.0)*(a.real + b.real)) / x**2
  return Q_ext

#@njit((complex128, complex128, float64, float64), cache=True)
def _calc_extinction_efficiency_coated_scalar(m_1, m_2, x, y):
  a, b = _mie_An_Bn_coated(m_1, m_2, x, y)
  n = np.arange(1, len(a)+1)

  Q_ext = 2*np.sum((2.0*n + 1.0)*(a.real + b.real)) / y**2
  return Q_ext

#@njit((complex128, complex128, float64, float64[:]), cache=True)
def calc_extinction_coefficient_for_sphere(N_particle, N_medium, radius, wavelength_vacuo):
  m = N_particle / N_medium # May need to be changed into something calculated
  x = 2*np.pi*N_medium*radius/wavelength_vacuo

  if np.isscalar(wavelength_vacuo):
    return _calc_extinction_efficiency_scalar(m, x)
  
  no_data_points = len(wavelength_vacuo)
  c_ext = np.empty(no_data_points, dtype=np.float64)
  for i in range(no_data_points):
    c_ext[i] = _calc_extinction_efficiency_scalar(m[i], x[i])*np.pi*radius**2
  
  return c_ext

#@njit((complex128, complex128, complex128, float64, float64, float64[:]), cache=True)
def calc_extinction_coefficient_for_coated_sphere(N_particle, N_coat, N_medium, particle_radius, coat_radius, wavelength_vacuo):
  m_1 = N_particle / N_medium
  m_2 = N_coat / N_medium
  x = 2*np.pi*particle_radius/wavelength_vacuo
  y = 2*np.pi*coat_radius/wavelength_vacuo

  if np.isscalar(wavelength_vacuo):
    return _calc_extinction_efficiency_coated_scalar(m_1, m_2, x, y)
  
  no_data_points = len(wavelength_vacuo)
  c_ext = np.empty(no_data_points, dtype=np.float64)
  for i in range(no_data_points):
    c_ext[i] = _calc_extinction_efficiency_coated_scalar(m_1[i], m_2[i], x[i], y[i])
  return c_ext

def calc_extinction_for_a_slab_of_particles(particle_number_density, thickness, c_ext):
  absorbance = particle_number_density*thickness*c_ext

  if absorbance >= 1:
    print("Calculation is likely invalid due to effect of multiscattering")

  return np.exp(-absorbance)

