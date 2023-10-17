# Assume there is a function in pylablib to control the filter
from pylablib import set_filter_wavelength

def add_to_gui(gui):
    # Create a button and a text box to set the wavelength
    wavelength_input = QLineEdit(gui)
    wavelength_input.move(220, 20)
    btnSetWavelength = QPushButton('Set Wavelength', gui)
    btnSetWavelength.move(220, 50)
    btnSetWavelength.clicked.connect(lambda: set_filter_wavelength(float(wavelength_input.text())))
