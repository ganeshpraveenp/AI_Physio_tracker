# Physiotherapy & Elbow ROM Exercise Tracker

A Flask-based web application for tracking patient physiotherapy exercises—specifically Elbow Passive Range of Motion (PROM)—using real-time computer vision, pose estimation, and repetition counting.

## Features

- **Patient Authentication & Onboarding**: Secure user registration and login system storing patient profiles (name, age, sex, weight, height, injury cause, and exercise start date) in a local SQLite database.
- **Real-Time Pose Estimation**: Uses OpenCV and MediaPipe Pose to track shoulder, elbow, and wrist landmarks live via webcam.
- **Automated Repetition & Form Tracking**: Calculates joint angles in real time to validate arm alignment, count completed repetitions against a customizable target, and display live feedback on the video stream.
- **Interactive Dashboard**: Provides authenticated access to patient dashboards and exercise modules.

## Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite3
- **Computer Vision**: OpenCV (`opencv-python`), MediaPipe (`mediapipe`), NumPy

## Project Structure

```text
├── app.py              # Main Flask application, routes, and database initialization
├── elbow_tracker.py    # OpenCV & MediaPipe pose detection and rep-counting logic
├── database.db         # SQLite database (auto-generated on first run)
└── templates/          # HTML templates (login.html, register.html, dashboard.html, elbow.html)
```

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd <repository-folder>
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask opencv-python mediapipe numpy
   ```

4. **Run the application**
   ```bash
   python app.py
   ```
   The app will automatically initialize `database.db` and start on `http://127.0.0.1:5000/`.

## Usage

1. Navigate to `http://127.0.0.1:5000/` and register a new patient account.
2. Log in with your credentials to access the dashboard.
3. Open the **Elbow PROM** module (`/exercise/elbow_prom`), set your target repetition count, and allow webcam access to begin tracking.

## Notes

- Ensure a working webcam is connected and accessible at device index `0`.
- Remember to update `app.secret_key` in `app.py` and implement password hashing (e.g., `werkzeug.security`) before deploying to production.
- Add `database.db` and `venv/` to your `.gitignore` file to avoid committing local database records or environment files.
