from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QLineEdit, QComboBox
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QLineEdit, QComboBox, QFileDialog

from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
import sys
import requests
import numpy as np  # Placeholder for image array; replace as needed

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Microscope Control")
        self.setGeometry(100, 100, 800, 600)

        # GUI for camera feed
        self.imageLabel = QLabel(self)
        self.imageLabel.resize(640, 480)
        self.imageLabel.move(20, 100)

        self.cameraSelector = QComboBox(self)
        self.cameraSelector.addItem("Camera 1")
        self.cameraSelector.addItem("Camera 2")
        self.cameraSelector.move(20, 60)

        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.update_camera_feed)
        self.updateTimer.start(50)  # 50 ms refresh rate

        # Video Duration Input
        self.txtVideoDuration = QLineEdit(self)
        self.txtVideoDuration.move(700, 400)
        self.txtVideoDuration.setPlaceholderText("Video Duration (sec)")

        # Timelapse Interval Input
        self.txtTimelapseInterval = QLineEdit(self)
        self.txtTimelapseInterval.move(700, 450)
        self.txtTimelapseInterval.setPlaceholderText("Timelapse Interval (sec)")

        # Start Video Button
        self.btnStartVideo = QPushButton('Start Video', self)
        self.btnStartVideo.move(700, 300)
        self.btnStartVideo.clicked.connect(self.start_video)

        # Start Timelapse Button
        self.btnStartTimelapse = QPushButton('Start Timelapse', self)
        self.btnStartTimelapse.move(700, 350)
        self.btnStartTimelapse.clicked.connect(self.start_timelapse)

    def update_camera_feed(self):
        camera_id = self.cameraSelector.currentIndex() + 1
        frame = self.get_image_from_camera(camera_id)  # Replace this with the actual pylablib or ThorLabs API call

        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.imageLabel.setPixmap(pixmap)

    def get_image_from_camera(self, camera_id):
        # This is a placeholder function; replace with the actual pylablib or ThorLabs API call
        return np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

    def start_video(self):
        camera_id = self.cameraSelector.currentIndex() + 1
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self,"Save Video","","MP4 Files (*.mp4);;AVI Files (*.avi)", options=options)
        if filename:
            duration = self.txtVideoDuration.text()  # retrieve duration from textbox
            response = requests.post("http://localhost:8000/start_video", data={"camera_id": camera_id, "filename": filename, "duration": duration})
            response_data = jsonify(response.text)
            # Optional: Show a message box or notification about the status

    def start_timelapse(self):
        camera_id = self.cameraSelector.currentIndex() + 1
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self,"Save Timelapse","","MP4 Files (*.mp4);;AVI Files (*.avi)", options=options)
        if filename:
            interval = self.txtTimelapseInterval.text()  # retrieve interval from textbox
            duration = 60  # you can also add another textbox to get user input for the duration
            response = requests.post("http://localhost:8000/start_timelapse", data={"camera_id": camera_id, "filename": filename, "interval": interval, "duration": duration})
            response_data = jsonify(response.text)
            # Optional: Show a message box or notification about the status

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())
