import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

mp_drawing = mp.solutions.drawing_utils

rep_count = 0
stage = None
message = "Start Exercise"


def calculate_angle(a, b, c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180:
        angle = 360-angle

    return angle


def process_frame(frame):

    global rep_count, stage, message

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    if not results.pose_landmarks:
        message = "Elbow not visible"
        return frame, rep_count, message

    landmarks = results.pose_landmarks.landmark

    # Coordinates
    shoulder = [
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y
    ]

    elbow = [
        landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y
    ]

    wrist = [
        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y
    ]

    angle = calculate_angle(shoulder, elbow, wrist)

    # Rep logic
    if angle > 160:
        stage = "down"
        message = "Arm extended"

    if angle < 40 and stage == "down":
        stage = "up"
        rep_count += 1
        message = f"{rep_count} Rep Completed"

    if 40 < angle < 160:
        message = "Adjust arm position"

    # Draw skeleton
    mp_drawing.draw_landmarks(
        frame,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )

    h, w, _ = frame.shape

    # Convert to pixel coordinates
    elbow_pixel = tuple(np.multiply(elbow, [w, h]).astype(int))
    shoulder_pixel = tuple(np.multiply(shoulder, [w, h]).astype(int))
    wrist_pixel = tuple(np.multiply(wrist, [w, h]).astype(int))

    # Highlight arm joints
    cv2.circle(frame, shoulder_pixel, 8, (0,255,0), -1)
    cv2.circle(frame, elbow_pixel, 8, (0,0,255), -1)
    cv2.circle(frame, wrist_pixel, 8, (255,0,0), -1)

    # Display angle
    cv2.putText(
        frame,
        str(int(angle)),
        elbow_pixel,
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255,255,255),
        2,
        cv2.LINE_AA
    )

    return frame, rep_count, message