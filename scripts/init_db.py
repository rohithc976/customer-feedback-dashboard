import sys
import os

# Add parent directory to python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from werkzeug.security import generate_password_hash
from config import Config
from app.database import init_db

def create_admin_user():
    """Create default administrator account if one does not already exist."""
    db_path = Config.DATABASE_PATH
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    default_username = 'admin'
    default_password = 'admin123'

    cursor.execute("SELECT id FROM users WHERE username = ?", (default_username,))
    existing = cursor.fetchone()

    if not existing:
        password_hash = generate_password_hash(default_password)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (default_username, password_hash)
        )
        conn.commit()
        print(f"[SUCCESS] Admin account created successfully!")
        print(f"          Username : {default_username}")
        print(f"          Password : {default_password}")
    else:
        print(f"[INFO] Admin user '{default_username}' already exists in database.")

    conn.close()

if __name__ == '__main__':
    print("--------------------------------------------------")
    print(" Initializing Customer Feedback Database (SQLite)")
    print("--------------------------------------------------")
    init_db()
    print("[SUCCESS] Database tables ('users', 'feedback') verified.")
    create_admin_user()
    print("--------------------------------------------------")
    print("Initialization completed successfully!")
