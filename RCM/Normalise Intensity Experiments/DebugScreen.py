import ExperimentGUI

class DebugScreen(ExperimentGUI.ExperimentGUI):
  def __init__(self, greyscale=255, do_overrideredirect=True, current_mA=100, image_path=""):
    super().__init__(greyscale=greyscale, current_mA=current_mA, do_overrideredirect=do_overrideredirect)
    if image_path != "":
      bg = tk.PhotoImage(file=image_path)
      self.canvas.create_image(0, 0, image=bg, anchor="nw")

    print("Press 'f' to move screen to projector monitor and activate full screen")
    print("Press 'l' to obtain reading from power meter")
    print("Press 'g' to change greyscale values")
    print("Press 'e' to end experiment")

    self.bind("<Key>", self.key_press)

    self.mainloop()
  
  def key_press(self, event):
    if event.char == "l":
      print(self.power_meter.get_power_reading_W_str())
    elif event.char == "f":
      self.activate_full_screen()
    elif event.char == "g":
      greyscale = int(input("Enter new greyscale value (0-255): "))
      if type(greyscale) != type(1) or greyscale < 0 or greyscale > 255:
        print("Not a valid greyscale value!")
      else:
        self.canvas.config(bg=f"#{greyscale:02X}{greyscale:02X}{greyscale:02X}")
    elif event.char == "e":
      self.destroy()