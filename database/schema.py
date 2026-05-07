import sqlite3

DB_PATH = "aarogya.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            village TEXT NOT NULL,
            district TEXT DEFAULT '',
            language TEXT DEFAULT 'Hindi',
            conditions TEXT DEFAULT '',
            allergies TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS diagnoses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            image_path TEXT DEFAULT '',
            symptom_description TEXT NOT NULL,
            raw_response TEXT NOT NULL,
            conditions TEXT DEFAULT '',
            urgency TEXT DEFAULT '',
            next_steps TEXT DEFAULT '',
            red_flags TEXT DEFAULT '',
            model_used TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            dose TEXT NOT NULL,
            frequency TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT DEFAULT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS adherence_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            status TEXT NOT NULL,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (medication_id) REFERENCES medications(id),
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            UNIQUE(medication_id, log_date)
        );
    """)
    conn.commit()
    conn.close()
