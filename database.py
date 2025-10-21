
import sqlite3

DB_FILE = "candidates.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            linkedin_profile TEXT,
            summary TEXT,
            skills TEXT,
            experience TEXT,
            education TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_or_update_candidate(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM candidates WHERE name=?", (data["name"],))
    row = c.fetchone()
    if row:
        c.execute("""
            UPDATE candidates SET email=?, phone=?, linkedin_profile=?, summary=?, skills=?, experience=?, education=?
            WHERE id=?
        """, (data["email"], data["phone"], data["linkedin_profile"], data["summary"], 
              ",".join(data["skills"]), ",".join(data["experience"]), ",".join(data["education"]), row[0]))
    else:
        c.execute("""
            INSERT INTO candidates (name, email, phone, linkedin_profile, summary, skills, experience, education)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (data["name"], data["email"], data["phone"], data["linkedin_profile"], data["summary"],
              ",".join(data["skills"]), ",".join(data["experience"]), ",".join(data["education"])))
    conn.commit()
    conn.close()

def get_all_candidate_names():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name FROM candidates")
    names = [row[0] for row in c.fetchall()]
    conn.close()
    return names

def get_candidate_by_name(name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM candidates WHERE name=?", (name,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "phone": row[3],
            "linkedin_profile": row[4],
            "summary": row[5],
            "skills": row[6].split(",") if row[6] else [],
            "experience": row[7].split(",") if row[7] else [],
            "education": row[8].split(",") if row[8] else []
        }
    return None

def delete_candidate_by_name(name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM candidates WHERE name=?", (name,))
    conn.commit()
    conn.close()
