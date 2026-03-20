import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Add new columns for advanced metrics
cursor.execute("ALTER TABLE exercise_results ADD COLUMN correct_reps INTEGER DEFAULT 0")
cursor.execute("ALTER TABLE exercise_results ADD COLUMN max_flexion INTEGER DEFAULT 0")
cursor.execute("ALTER TABLE exercise_results ADD COLUMN max_extension INTEGER DEFAULT 0")
cursor.execute("ALTER TABLE exercise_results ADD COLUMN rom INTEGER DEFAULT 0")
cursor.execute("ALTER TABLE exercise_results ADD COLUMN avg_time REAL DEFAULT 0")
cursor.execute("ALTER TABLE exercise_results ADD COLUMN form_score INTEGER DEFAULT 0")

conn.commit()
conn.close()

print("Database updated successfully!")
