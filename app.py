from flask import Flask, render_template, Response, request,session,redirect
import cv2
from elbow_tracker import process_frame
import elbow_tracker
import sqlite3
import time
from reportlab.pdfgen import canvas
from flask import send_file
import io
current_exercise = "elbow"   # default

app = Flask(__name__)
app.secret_key = "physio_secret_key"

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
    full_name TEXT,
    age INTEGER,
    sex TEXT,
    height REAL,
    weight REAL,
    therapy_cause TEXT,
    therapy_since TEXT,
    email TEXT UNIQUE,
    password TEXT
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
    global rep_count, message, started, target_reps, current_exercise

    while True:
        success, frame = cap.read()
        if not success:
            break

        if started:

            # 🔁 SWITCH BETWEEN EXERCISES
            if current_exercise == "elbow":
                frame, rep_count, message = elbow_tracker.process_frame(frame)

            elif current_exercise == "squat":
                import squat_tracker
                frame, rep_count, message = squat_tracker.process_frame(frame)

            elif current_exercise == "shoulder":
                import shoulder_tracker
                frame, rep_count, message = shoulder_tracker.process_frame(frame)

            else:
                message = "Unknown Exercise"

            # ✅ STOP WHEN TARGET COMPLETED
            if rep_count >= target_reps:
                message = "Target Completed"
                started = False
               

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/")
def home():
    return redirect("/login")                           #home


from flask import request, redirect
import sqlite3

patient_id = None



@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")                         #login_page
        cursor = conn.cursor()

        cursor.execute(
        "SELECT * FROM patients WHERE email=? AND password=?",
        (email,password))

        user = cursor.fetchone()

        conn.close()

        if user:
            session["patient_id"] = user[0]
            return redirect("/dashboard")
        else:
             return "Invalid email or password"

    return render_template("login.html")



@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        age = request.form["age"]
        sex = request.form["sex"]
        height = request.form["height"]
        weight = request.form["weight"]                              #register_page
        therapy_cause = request.form["therapy_cause"]
        therapy_since = request.form["therapy_since"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")

        conn.execute("""
        INSERT INTO patients
        (full_name, age, sex, height, weight, therapy_cause, therapy_since, email, password)
        VALUES (?,?,?,?,?,?,?,?,?)
        """,(full_name,age,sex,height,weight,therapy_cause,therapy_since,email,password))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():

    if "patient_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html")

#_____________________________________________________________________________________________________________________#

 #ELBOW EXERCISE 

@app.route("/exercise")
def exercise():
    exercise_type = request.args.get("exercise", "elbow")  # default = elbow
    return render_template("index.html", exercise=exercise_type)


@app.route("/video_feed")                                         #vedio
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/start", methods=["POST"])
def start():
    global started, target_reps, rep_count, start_time, message, current_exercise

    # 🔥 RESET EVERYTHING
    rep_count = 0
    message = "Starting..."
    started = True

    target_reps = int(request.form["target"])
    current_exercise = request.form["exercise"]

    start_time = time.time()

    return ("", 204)

@app.route("/status")
def status():

    global rep_count, message, target_reps

    completed = False

    if target_reps > 0 and rep_count >= target_reps:                              #status_box
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
 #___________________________________________________________________________________________________________________#




from datetime import datetime
@app.route("/save_result", methods=["POST"])
def save_result():
    import sqlite3
    from datetime import datetime

    global start_time, target_reps, current_exercise, rep_count, started

    print("Result saved")

    patient_id = session["patient_id"]

    # ⏱ Time taken
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    # 🔥 SELECT CORRECT TRACKER
    if current_exercise == "elbow":
        import elbow_tracker
        report = elbow_tracker.get_exercise_report()

    elif current_exercise == "squat":
        import squat_tracker
        report = squat_tracker.get_exercise_report()

    elif current_exercise == "shoulder":
        import shoulder_tracker
        report = shoulder_tracker.get_exercise_report()

    else:
        return {"error": "Unknown exercise"}

    # 💾 Save to DB
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO exercise_results
    (patient_id, exercise, target_reps, completed_reps, correct_reps,
     accuracy, time_taken, max_flexion, max_extension, rom,
     avg_time, form_score, date)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        patient_id,
        report["exercise"],
        target_reps,
        report["reps_completed"],
        report["correct_reps"],
        round(report["score"], 2),
        time_taken,
        report["max_flexion"],
        report["max_extension"],
        report["rom"],
        report["avg_time"],
        report["score"],
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    # 🔥 RESET STATE (VERY IMPORTANT)
    rep_count = 0
    target_reps = 0
    started = False

    return {"status": "saved"}

@app.route("/results")
def results():
    import sqlite3

    patient_id = session["patient_id"]   # get logged-in user id

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT patients.full_name,
           patients.email,
           exercise_results.exercise,
           exercise_results.target_reps,
           exercise_results.completed_reps,
           exercise_results.correct_reps,
           exercise_results.accuracy,
           exercise_results.time_taken,
           exercise_results.max_flexion,
           exercise_results.max_extension,
           exercise_results.rom,
           exercise_results.avg_time,
           exercise_results.form_score,
           exercise_results.date
    FROM exercise_results
    JOIN patients
    ON exercise_results.patient_id = patients.id
    WHERE patients.id = ?
    """, (patient_id,))

    data = cursor.fetchall()
    conn.close()

    return render_template("results.html", data=data)


@app.route("/report")
def report():

    patient_id = session["patient_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
    patient = cursor.fetchone()

    cursor.execute("""
    SELECT exercise, target_reps, completed_reps, correct_reps,
           accuracy, max_flexion, max_extension, rom,
           avg_time, form_score, date
    FROM exercise_results
    WHERE patient_id=?
    """, (patient_id,))

    results = cursor.fetchall()
    conn.close()

    import io
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)

    # 🔹 Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(170, 800, "Physiotherapy Report")

    # 🔹 Patient Details
    pdf.setFont("Helvetica", 9)
    pdf.drawString(50, 760, f"Name: {patient[1]}")
    pdf.drawString(50, 740, f"Age: {patient[2]}")
    pdf.drawString(50, 720, f"Sex: {patient[3]}")
    pdf.drawString(50, 700, f"Height: {patient[4]}")
    pdf.drawString(50, 680, f"Weight: {patient[5]}")
    pdf.drawString(50, 660, f"Cause: {patient[6]}")

    pdf.line(50, 650, 800, 650)

    # 🔹 Table Title
    y = 620
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Exercise Results")

    # 🔹 Table Header (SMALL FONT to fit all)
    y -= 25
    pdf.setFont("Helvetica-Bold", 7)

    pdf.drawString(50, y, "Exercise")
    pdf.drawString(100, y, "Tar")
    pdf.drawString(120, y, "Comp")
    pdf.drawString(160, y, "Corr")
    pdf.drawString(200, y, "Acc")
    pdf.drawString(240, y, "Flex")
    pdf.drawString(280, y, "Ext")
    pdf.drawString(320, y, "ROM")
    pdf.drawString(360, y, "Time")
    pdf.drawString(400, y, "Form")
    pdf.drawString(450, y, "Date")

    y -= 10
    pdf.line(50, y, 550, y)

    # 🔹 Data
    pdf.setFont("Helvetica", 7)
    y -= 15

    for r in results:
        pdf.drawString(50, y, str(r[0]))
        pdf.drawString(100, y, str(r[1]))
        pdf.drawString(120, y, str(r[2]))
        pdf.drawString(160, y, str(r[3]))
        pdf.drawString(200, y, f"{r[4]}%")
        pdf.drawString(240, y, f"{r[5]}°")
        pdf.drawString(280, y, f"{r[6]}°")
        pdf.drawString(320, y, f"{r[7]}°")
        pdf.drawString(360, y, f"{r[8]}s")
        pdf.drawString(400, y, f"{r[9]}%")
        pdf.drawString(450, y, str(r[10]))

        y -= 18

        # 🔹 New page if overflow
        if y < 40:
            pdf.showPage()
            pdf.setFont("Helvetica", 7)
            y = 800

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="physio_report.pdf",
        mimetype='application/pdf'
    )



if __name__ == "__main__":
    app.run(debug=True)