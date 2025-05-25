from flask import Flask, render_template, Response, jsonify
from flask_socketio import SocketIO
import cv2
from detection import detect_drowsiness_and_yawning

app = Flask(__name__)
socketio = SocketIO(app)

camera = None
is_running = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    global camera, is_running
    if not is_running or camera is None or not camera.isOpened():
        return "Camera not running", 403
    return Response(detect_drowsiness_and_yawning(camera, socketio),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start')
def start():
    global camera, is_running
    if not is_running:
        camera = cv2.VideoCapture(0)
        is_running = True
    return jsonify({"status": "started"})

@app.route('/stop')
def stop():
    global camera, is_running
    if is_running and camera is not None:
        camera.release()
        camera = None
        is_running = False
    return jsonify({"status": "stopped"})

if __name__ == '__main__':
    socketio.run(app, debug=True)
