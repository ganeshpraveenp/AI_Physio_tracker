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
        message = "Shoulder not visible"
        return frame, rep_count, message

    landmarks = results.pose_landmarks.landmark

    # 🔥 Using LEFT arm for variety (you can change to RIGHT if needed)
    shoulder = [
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
    ]

    elbow = [
        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y
    ]

    wrist = [
        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y
    ]

    # 🔥 SHOULDER RAISE ANGLE (same calculation)
    angle = calculate_angle(shoulder, elbow, wrist)

    # Track max extension & flexion
    if angle > max_extension:
        max_extension = angle

    if angle < max_flexion:
        max_flexion = angle

    # 🔥 DOWN (arm straight down)
    if angle > 150:
        stage = "down"
        message = "Arm down"

    # 🔥 UP (arm raised)
    if angle < 60 and stage == "down":
        stage = "up"
        rep_count += 1

        # ⏱ timing
        if rep_start_time is not None:
            rep_time = time.time() - rep_start_time
            rep_times.append(rep_time)

        rep_start_time = time.time()

        # ✔ form check
        if angle < 50:
            correct_rep += 1
            message = f"Rep {rep_count} ✔ Good raise"
        else:
            message = f"Rep {rep_count} ⚠ Raise higher"

    # Middle
    if 60 < angle < 150:
        message = "Raise your arm"

    # Draw skeleton
    mp_drawing.draw_landmarks(
        frame,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )

    h, w, _ = frame.shape

    elbow_pixel = tuple(np.multiply(elbow, [w, h]).astype(int))
    shoulder_pixel = tuple(np.multiply(shoulder, [w, h]).astype(int))
    wrist_pixel = tuple(np.multiply(wrist, [w, h]).astype(int))

    cv2.circle(frame, shoulder_pixel, 8, (0,255,0), -1)
    cv2.circle(frame, elbow_pixel, 8, (0,0,255), -1)
    cv2.circle(frame, wrist_pixel, 8, (255,0,0), -1)

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


# 📊 REPORT (same format as elbow)
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
        "exercise": "Shoulder Raise",
        "reps_completed": rep_count,
        "correct_reps": correct_rep,
        "max_flexion": int(max_flexion),
        "max_extension": int(max_extension),
        "rom": int(ROM),
        "avg_time": round(avg_rep_time, 2),
        "score": form_score
    }

    return report


# 🔁 RESET FUNCTION (VERY IMPORTANT)
def reset():
    global rep_count, correct_rep, stage, message
    global max_extension, max_flexion
    global rep_times, rep_start_time

    rep_count = 0
    correct_rep = 0
    stage = None
    message = "Start Exercise"
    max_extension = 0
    max_flexion = 180
    rep_times = []
    rep_start_time = None