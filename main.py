import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Define landmark indices
LEFT_EYE_LANDMARKS = [33, 159, 145, 133, 153, 144]  # Left eye
RIGHT_EYE_LANDMARKS = [362, 386, 374, 263, 373, 380]  # Right eye
MOUTH_LANDMARKS = [61, 291, 78, 308, 13, 14]  # Adjusted mouth landmarks for better detection

# Define thresholds
EAR_THRESHOLD = 0.25  # Eye Aspect Ratio threshold for drowsiness
MAR_THRESHOLD = 0.8  # Adjusted Mouth Aspect Ratio threshold for yawning
EAR_FRAMES = 15  # Number of consecutive frames for drowsiness detection

frame_counter = 0  # Counter for closed eyes duration
yawn_counter = 0  # Counter for yawning duration


def aspect_ratio(landmarks, indices, width, height):
    """Calculates aspect ratio for eyes or mouth using only 6 points."""
    points = [np.array([landmarks[i].x * width, landmarks[i].y * height]) for i in indices]
    
    vertical_distance_1 = np.linalg.norm(points[1] - points[2])
    vertical_distance_2 = np.linalg.norm(points[4] - points[5])
    horizontal_distance = np.linalg.norm(points[0] - points[3])
    
    return (vertical_distance_1 + vertical_distance_2) / (2.0 * horizontal_distance)

# OpenCV Video Capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    height, width, _ = frame.shape

    # Process frame with MediaPipe
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Calculate EAR (Eye Aspect Ratio)
            left_EAR = aspect_ratio(face_landmarks.landmark, LEFT_EYE_LANDMARKS, width, height)
            right_EAR = aspect_ratio(face_landmarks.landmark, RIGHT_EYE_LANDMARKS, width, height)
            avg_EAR = (left_EAR + right_EAR) / 2.0

            # Calculate MAR (Mouth Aspect Ratio)
            MAR = aspect_ratio(face_landmarks.landmark, MOUTH_LANDMARKS, width, height)

            # Detect drowsiness
            if avg_EAR < EAR_THRESHOLD:
                frame_counter += 1
                if frame_counter >= EAR_FRAMES:
                    cv2.putText(frame, "DROWSY!", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            else:
                frame_counter = 0

            # Detect yawning
            if MAR > MAR_THRESHOLD:
                yawn_counter += 1
                if yawn_counter >= 10:  # Yawn detected over multiple frames for reliability
                    cv2.putText(frame, "YAWNING!", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)
            else:
                yawn_counter = 0

            # Draw landmarks
            for i in LEFT_EYE_LANDMARKS + RIGHT_EYE_LANDMARKS + MOUTH_LANDMARKS:
                x, y = int(face_landmarks.landmark[i].x * width), int(face_landmarks.landmark[i].y * height)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            # Display EAR and MAR values
            cv2.putText(frame, f"EAR: {avg_EAR:.2f}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(frame, f"MAR: {MAR:.2f}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Show frame
    cv2.imshow("Drowsiness and Yawning Detection", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()