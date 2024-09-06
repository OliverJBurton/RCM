
from oceandirect.OCeanDirectAPI import OceanDirectAPI, OceanDirectError, FeatureID


#Spectrometer code to input gain, exposure time, repeats to return counts vs wavelength

# Check product manual appendix A for meaning of error codes
# https://www.oceanoptics.com/wp-content/uploads/2024/05/MNL-1025-OceanDirect-User-Manual-060822.pdf?_gl=1*xv9znt*_up*MQ..*_ga*NzM5MDU4NjcwLjE3MjU2MjI1NTA.*_ga_R56J7LLTX4*MTcyNTYyMjU0OS4xLjAuMTcyNTYyMjU0OS4wLjAuNjkyMzg2NjI4

class Ocean_Spectrometer(OceanDirectAPI):
  def __init__(self):
    try:
      device_count = self.find_usb_devices()

      if device_count == 0:
        raise RuntimeError("No ocean spectroscopes found")

      device_ids = self.get_device_ids()
      print("Device id: ", device_ids)

      if device_count > 1:
        print("More than 1 devices detected, selecting first device")

      self.device_id = device_ids[0]
      self.device = self.open_device(self.device_id)
      self.serial_number = self.device.get_serial_number()

      print(f"Device with serial number {self.serial_number} has been initialised.")
    except OceanDirectError as err:
      [errorCode, errorMsg] = err.get_error_details()
      print(f"Ocean_Spectrometer initialisation has failed: {errorCode} | {errorMsg}")
  
  def close_device(self):
    self.close_device(self.device_id)
    self.shutdown()
  
  def read_spectra(integrationTimeUs: int, spectraToRead: int):
    # Do a set scan to average

    '''
    Return spectrum measured by spectrometer

    :param integrationTimeUs: length of time during which light is allowed to pass into the spectrometer's detector. Too high can lead to saturation. Too low would prevent the taking of a meaningful spectra.


    '''

    try:
      self.device.set_integration_time(integrationTimeUs)

      output = []
      for i in range(spectraToRead):
        spectra = device.get_formatted_spectrum()
        output.append(spectra)
      
      return output
    except OceanDirectError as err:
      [errorCode, errorMsg] = err.get_error_details()
      print(f"Ocean_Spectrometer.read_spectra() exception: {errorCode} | {errorMsg}")

