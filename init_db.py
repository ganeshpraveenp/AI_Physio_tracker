import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Patients table
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

# Exercise results table (with advanced metrics)
cursor.execute("""
CREATE TABLE IF NOT EXISTS exercise_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    exercise TEXT,
    target_reps INTEGER,
    completed_reps INTEGER,
    correct_reps INTEGER DEFAULT 0,
    accuracy REAL,
    time_taken REAL,
    max_flexion INTEGER DEFAULT 0,
    max_extension INTEGER DEFAULT 0,
    rom INTEGER DEFAULT 0,
    avg_time REAL DEFAULT 0,
    form_score INTEGER DEFAULT 0,
    date TEXT
)
""")

conn.commit()
conn.close()