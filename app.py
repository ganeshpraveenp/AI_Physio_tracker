from flask import Flask, render_template, Response, request
import cv2
from elbow_tracker import process_frame
import sqlite3
import time

app = Flask(__name__)

cap = cv2.VideoCapture(0)

target_reps = 10
rep_count = 0
message = "Waiting to start..."
started = False
start_time = None
patient_id = None
target_reps = 0





import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    register_id TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS exercise_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    exercise TEXT,
    target_reps INTEGER,
    completed_reps INTEGER,
    accuracy REAL,
    time_taken REAL,
    date TEXT
)
""")

conn.commit()
conn.close()





def generate_frames():
    global rep_count, message, started, target_reps

    while True:
        success, frame = cap.read()
        if not success:
            break

        if started:
            frame, rep_count, message = process_frame(frame)

            # STOP VIDEO WHEN TARGET REPS COMPLETED
            if rep_count >= target_reps:
                message = "Target Completed"
                started = False
                break

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/")
def index():
    return render_template("register.html")                           #home_register


from flask import request, redirect
import sqlite3

patient_id = None


@app.route("/register", methods=["GET","POST"])
def register():

    global patient_id

    if request.method == "POST":

        name = request.form["name"]
        register_id = request.form["register_id"]

        conn = sqlite3.connect("database.db")                        #register
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO patients (name, register_id) VALUES (?, ?)",
            (name, register_id)
        )

        patient_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return redirect("/exercise")

    return render_template("register.html")


@app.route("/exercise")
def exercise():
    return render_template("index.html")


@app.route("/video_feed")                                         #vedio
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/start", methods=["POST"])
def start():

    global started, target_reps, rep_count, start_time, message

    started = True
    rep_count = 0
    target_reps = int(request.form["target"])

    start_time = time.time()     # start exercise timer
    message = "Exercise Started"

    return ("", 204)


@app.route("/status")
def status():

    global rep_count, message, target_reps

    completed = False

    if target_reps > 0 and rep_count >= target_reps:
        completed = True

    return {
        "reps": rep_count,
        "msg": message,
        "completed": completed
    }


@app.route("/start_page", methods=["POST"])                             
def start_timer():

    global start_time, target_reps                                #time

    target_reps = int(request.form["target"])
    start_time = time.time()

    return ("",204)


from datetime import datetime

@app.route("/save_result", methods=["POST"])
def save_result():
    print("Result saved")

    global rep_count, start_time, target_reps, patient_id

    end_time = time.time()
    time_taken = round(end_time - start_time,2)

    accuracy = (rep_count / target_reps) * 100                              #save_result

    conn = sqlite3.connect("database.db")

    conn.execute("""
    INSERT INTO exercise_results
    (patient_id, exercise, target_reps, completed_reps, accuracy, time_taken, date)
    VALUES (?,?,?,?,?,?,?)
    """,(patient_id,"Elbow Flexion",target_reps,rep_count,accuracy,time_taken,
        datetime.now().strftime("%Y-%m-%d")))

    conn.commit()
    conn.close()

    return {"status":"saved"}




@app.route("/results")
def results():

    import sqlite3

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()                                              #result_page

    cursor.execute("""
    SELECT patients.name,
           patients.register_id,
           exercise_results.exercise,
           exercise_results.target_reps,
           exercise_results.completed_reps,
           exercise_results.accuracy,
           exercise_results.time_taken,
           exercise_results.date
    FROM exercise_results
    JOIN patients
    ON exercise_results.patient_id = patients.id
    """)

    data = cursor.fetchall()

    conn.close()

    return render_template("results.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)