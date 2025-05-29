from flask import Flask, render_template, Response, jsonify, request
from flask_socketio import SocketIO
import cv2
import os
from detection import detect_drowsiness_and_yawning

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

camera = None
is_running = False
video_path = None

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

@app.route('/video_feed_file')
def video_feed_file():
    global video_path
    if not video_path or not os.path.exists(video_path):
        return "Video file not found", 404
    video_capture = cv2.VideoCapture(video_path)
    return Response(detect_drowsiness_and_yawning(video_capture, socketio),
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

@app.route('/upload', methods=['POST'])
def upload_video():
    global video_path
    file = request.files.get('video')
    if file:
        video_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(video_path)
        return jsonify({"status": "uploaded", "url": "/video_feed_file"})
    return jsonify({"status": "error", "message": "No file uploaded"}), 400

if __name__ == '__main__':
    socketio.run(app, debug=True)
