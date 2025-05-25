import cv2
import mediapipe as mp
import numpy as np
from flask_socketio import emit

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

LEFT_EYE_LANDMARKS = [33, 159, 145, 133, 153, 144]
RIGHT_EYE_LANDMARKS = [362, 386, 374, 263, 373, 380]
MOUTH_LANDMARKS = [61, 291, 78, 308, 13, 14]

EAR_THRESHOLD1 = 0.25
EAR_THRESHOLD2=0.21
MAR_THRESHOLD = 0.8
EAR_FRAMES = 15

frame_counter = 0
yawn_counter = 0
sleep_counter=0

def aspect_ratio(landmarks, indices, width, height):
    points = [np.array([landmarks[i].x * width, landmarks[i].y * height]) for i in indices]
    vertical1 = np.linalg.norm(points[1] - points[2])
    vertical2 = np.linalg.norm(points[4] - points[5])
    horizontal = np.linalg.norm(points[0] - points[3])
    return (vertical1 + vertical2) / (2.0 * horizontal)

def detect_drowsiness_and_yawning(camera, socketio):
    global frame_counter, yawn_counter, sleep_counter
    while camera.isOpened():
        try:
            success, frame = camera.read()
            if not success:
                continue
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = frame.shape
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    left_EAR = aspect_ratio(face_landmarks.landmark, LEFT_EYE_LANDMARKS, width, height)
                    right_EAR = aspect_ratio(face_landmarks.landmark, RIGHT_EYE_LANDMARKS, width, height)
                    avg_EAR = (left_EAR + right_EAR) / 2.0
                    MAR = aspect_ratio(face_landmarks.landmark, MOUTH_LANDMARKS, width, height)

                    if avg_EAR > EAR_THRESHOLD2 and avg_EAR < EAR_THRESHOLD1:
                        frame_counter += 1
                        if frame_counter >= EAR_FRAMES:
                        
                            cv2.putText(frame, "DROWSY!", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                            #emit('alert', 'DROWSY', broadcast=True)
                    else:
                        frame_counter = 0
                    
                    if avg_EAR <= EAR_THRESHOLD2:
                        sleep_counter += 1
                        if sleep_counter >= 10:
                            cv2.putText(frame, "SLEEPY", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                    else:
                        sleep_counter = 0
                
                    if MAR > MAR_THRESHOLD:
                        yawn_counter += 1
                        if yawn_counter >= 10:
                            cv2.putText(frame, "YAWNING!", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)
                    else:
                        yawn_counter = 0


                

                    for i in LEFT_EYE_LANDMARKS + RIGHT_EYE_LANDMARKS + MOUTH_LANDMARKS:
                        x, y = int(face_landmarks.landmark[i].x * width), int(face_landmarks.landmark[i].y * height)
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

                    cv2.putText(frame, f"EAR: {avg_EAR:.2f}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv2.putText(frame, f"MAR: {MAR:.2f}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        except Exception as e:
            print("Error in detection loop:", e)
            continue
