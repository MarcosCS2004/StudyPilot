import sqlite3
import os

db_path = 'backend/studypilot_dev.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email FROM users;")
        users = cursor.fetchall()
        print(f"Users found: {users}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("DB not found")
