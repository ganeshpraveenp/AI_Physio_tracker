
# Physiotherapy & Exercise ROM Tracker

A Flask-based web application for tracking physiotherapy exercises using computer vision and real-time movement analysis.

The application helps patients perform rehabilitation exercises, monitor their repetitions, track exercise performance, and maintain a history of physiotherapy sessions.

## Features

### Patient Authentication
- Patient registration and login.
- Secure password hashing using Werkzeug.
- Patient profile management.
- Patient information stored in SQLite.

### Computer Vision
- Real-time webcam-based exercise tracking.
- Pose estimation using OpenCV and MediaPipe.
- Joint movement and angle tracking.
- Automated repetition counting.
- Live exercise feedback.

### Supported Exercises
- Elbow Flexion (PROM)
- Shoulder Raise
- Mini Squats
- Knee Extension
- Arm Circles

### Exercise Tracking
- Customizable repetition targets.
- Completed and correct repetition tracking.
- Exercise accuracy and form score.
- Range of Motion (ROM) measurement.
- Exercise duration tracking.

### Patient Dashboard
- Personalized patient dashboard.
- Exercise session history.
- Patient profile and settings.
- Dark/light theme support.

### Reports
- Save exercise session results.
- View previous exercise sessions.
- Generate PDF physiotherapy reports.
- Download individual session reports.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Database |
| OpenCV | Computer vision |
| MediaPipe | Pose estimation |
| NumPy | Numerical calculations |
| Werkzeug | Password hashing |
| ReportLab | PDF report generation |
| HTML, CSS, JavaScript | Frontend |

## Project Structure

```text
project/
│
├── app.py
├── init_db.py
├── database.db
│
├── trackers/
│   ├── elbow_tracker.py
│   ├── shoulder_tracker.py
│   ├── squat_tracker.py
│   ├── knee_tracker.py
│   └── arm_circles_tracker.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── exercise.html
│   ├── profile.html
│   ├── settings.html
│   ├── results.html
│   ├── result_single.html
│   └── history.html
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <repository-folder>
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install flask opencv-python mediapipe numpy reportlab
```

Alternatively, install dependencies using:

```bash
pip install -r requirements.txt
```

### 5. Configure the Secret Key

Set a secure Flask secret key before running the application.

**Windows PowerShell:**

```powershell
$env:SECRET_KEY = "your-secret-key"
```

### 6. Run the Application

```bash
python app.py
```

Open your browser and navigate to:

http://127.0.0.1:5000/

## Usage

1. Open the application in your browser.
2. Register a new patient account.
3. Log in using your credentials.
4. Access the patient dashboard.
5. Select a physiotherapy exercise.
6. Set the target number of repetitions.
7. Allow webcam access.
8. Perform the exercise while following the live feedback.
9. Save the exercise session.
10. View exercise history and download PDF reports.

## Main Application Routes

| Route | Description |
|---|---|
| `/` | Redirects to login |
| `/register` | Patient registration |
| `/login` | Patient login |
| `/logout` | Logout |
| `/dashboard` | Patient dashboard |
| `/profile` | Patient profile |
| `/settings` | Account settings |
| `/exercise` | Exercise module |
| `/video_feed` | Live webcam feed |
| `/start` | Start exercise session |
| `/status` | Exercise status |
| `/save_result` | Save session results |
| `/results` | Exercise results |
| `/history` | Exercise history |
| `/report` | Download PDF report |
| `/report_single` | Download latest session report |

## Future Improvements

- Additional physiotherapy exercises.
- Improved pose estimation and movement accuracy.
- Personalized rehabilitation plans.
- Progress visualization and analytics.
- Cloud database integration.
- Mobile-friendly interface.

## Disclaimer

This application is developed for physiotherapy exercise tracking and educational purposes. It does not replace professional medical advice, diagnosis, or treatment. Patients should perform rehabilitation exercises under the guidance of a qualified healthcare professional.
