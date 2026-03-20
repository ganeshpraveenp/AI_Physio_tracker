import cv2
import mediapipe as mp
import numpy as np
import time

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

mp_drawing = mp.solutions.drawing_utils

# Exercise variables
correct_rep = 0
rep_count = 0
stage = None
message = "Start Exercise"

# Advanced tracking
max_extension = 0
max_flexion = 180
rep_times = []
rep_start_time = None


def calculate_angle(a, b, c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def process_frame(frame):

    global rep_count, stage, message, correct_rep
    global max_extension, max_flexion
    global rep_start_time, rep_times

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    if not results.pose_landmarks:
        message = "Body not visible"
        return frame, rep_count, message

    landmarks = results.pose_landmarks.landmark

    # RIGHT LEG POINTS
    hip = [
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y
    ]

    knee = [
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y
    ]

    ankle = [
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y
    ]

    angle = calculate_angle(hip, knee, ankle)

    # Track max extension (standing)
    if angle > max_extension:
        max_extension = angle

    # Track max flexion (lowest squat)
    if angle < max_flexion:
        max_flexion = angle

    # 👇 DOWN POSITION
    if angle < 90:
        stage = "down"
        message = "Go Up"

    # 👆 UP → REP COMPLETE
    if angle > 160 and stage == "down":
        stage = "up"
        rep_count += 1

        # Rep timing
        if rep_start_time is not None:
            rep_time = time.time() - rep_start_time
            rep_times.append(rep_time)

        rep_start_time = time.time()

        # Form check
        if angle > 165:
            correct_rep += 1
            message = f"Rep {rep_count} ✔ Good form"
        else:
            message = f"Rep {rep_count} ⚠ Stand straight"

    # Middle position
    if 90 <= angle <= 160:
        message = "Keep going"

    # Draw skeleton
    mp_drawing.draw_landmarks(
        frame,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )

    h, w, _ = frame.shape

    # Convert to pixel coordinates
    hip_pixel = tuple(np.multiply(hip, [w, h]).astype(int))
    knee_pixel = tuple(np.multiply(knee, [w, h]).astype(int))
    ankle_pixel = tuple(np.multiply(ankle, [w, h]).astype(int))

    # Highlight joints
    cv2.circle(frame, hip_pixel, 8, (0,255,0), -1)
    cv2.circle(frame, knee_pixel, 8, (0,0,255), -1)
    cv2.circle(frame, ankle_pixel, 8, (255,0,0), -1)

    # Display angle
    cv2.putText(
        frame,
        str(int(angle)),
        knee_pixel,
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255,255,255),
        2,
        cv2.LINE_AA
    )

    return frame, rep_count, message


def get_exercise_report():

    global rep_count, correct_rep
    global max_extension, max_flexion
    global rep_times

    ROM = max_extension - max_flexion

    if len(rep_times) > 0:
        avg_rep_time = sum(rep_times) / len(rep_times)
    else:
        avg_rep_time = 0

    if rep_count > 0:
        form_score = int((correct_rep / rep_count) * 100)
    else:
        form_score = 0

    report = {
        "exercise": "Squat",
        "reps_completed": rep_count,
        "correct_reps": correct_rep,
        "max_flexion": int(max_flexion),
        "max_extension": int(max_extension),
        "rom": int(ROM),
        "avg_time": round(avg_rep_time, 2),
        "score": form_score
    }

    return report