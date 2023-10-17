from flask import Flask, request, jsonify
import json

from pylablib.devices.Thorlabs import ThorlabsTLCamera as ThorlabsCamera
from pylablib.devices.Thorlabs import KinesisMotor as ThorlabsStage
import pylablib.devices.Thorlabs as tl
from time import sleep

app = Flask(__name__)

# Initialize stage and cameras; replace with actual device names or IDs
if 0:
    stage = ThorlabsStage("STAGE_DEVICE_NAME")
    camera1 = ThorlabsCamera("CAMERA1_DEVICE_NAME")
    camera2 = ThorlabsCamera("CAMERA2_DEVICE_NAME")

stage = 'stage'
camera1 = 'cam1'
camera2 = 'cam2'

@app.route('/set_objective', methods=['POST'])
def set_objective():
    """Set the microscope objective."""
    objective = request.form.get('objective')
    # Do the actual operations to set the objective
    return jsonify({"message": "Objective set", "objective": objective})

@app.route('/set_stage_position', methods=['POST'])
def set_stage_position():
    """Set the position of the stage."""
    x = float(request.form.get('x'))
    y = float(request.form.get('y'))
    z = float(request.form.get('z'))
    #stage.set_position(x, y, z)
    print(stage,x,y,z)
    return jsonify({"message": "Stage position set", "x": x, "y": y, "z": z})

@app.route('/start_video', methods=['POST'])
def start_video():
    """Start capturing video."""
    camera_id = request.form.get('camera_id')
    filename = request.form.get('filename')
    duration = float(request.form.get('duration'))  # In seconds

    camera = camera1 if camera_id == '1' else camera2
    #camera.capture_continuous(filename, duration)
    print(camera,duration)

    return jsonify({"message": "Video capturing started", "filename": filename, "duration": duration})

@app.route("/capture_image", methods=["POST"])
def capture_image():
    camera_id = request.form["camera_id"]
    filename = request.form["filename"]
    # Use pylablib or ThorLabs API to capture the image
    # YOUR_CODE_HERE
    return json.dumps({"status": "Image Captured"})
@app.route('/start_timelapse', methods=['POST'])
def start_timelapse():
    """Start capturing timelapse."""
    camera_id = request.form.get('camera_id')
    filename = request.form.get('filename')
    interval = float(request.form.get('interval'))  # In seconds
    duration = float(request.form.get('duration'))  # Total duration in seconds

    camera = camera1 if camera_id == '1' else camera2

    for _ in range(int(duration / interval)):
        #camera.capture_periodic(filename)
        print(camera)
        sleep(interval)

    return jsonify(
        {"message": "Timelapse capturing started", "filename": filename, "interval": interval, "duration": duration})


# More routes for capturing images, videos, etc.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
