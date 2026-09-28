import sqlite3
import os
from flask import g, current_app
from config import Config

def get_db():
    """
    Get a database connection for the current application context.
    Reuses connection stored in flask.g if available.
    """
    if 'db' not in g:
        db_path = current_app.config['DATABASE_PATH']
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        # Enable foreign keys
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    """Close the database connection if open."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app=None):
    """
    Initialize SQLite tables if they do not exist.
    Can be run from within Flask app or standalone CLI script.
    """
    if app:
        db_path = app.config['DATABASE_PATH']
    else:
        db_path = Config.DATABASE_PATH

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            product_service TEXT NOT NULL,
            category TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            message TEXT NOT NULL,
            sentiment TEXT NOT NULL CHECK(sentiment IN ('Positive', 'Neutral', 'Negative')),
            sentiment_score REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create indexes for search, filter & performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback(category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_sentiment ON feedback(sentiment);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at);")

    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    """
    Execute a parameterized SQL query and return results as dictionary/dictionaries.
    """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    if rv:
        if one:
            return dict(rv[0])
        return [dict(row) for row in rv]
    return None if one else []

def execute_db(query, args=()):
    """
    Execute an INSERT, UPDATE, or DELETE parameterized query and commit.
    Returns the last inserted row id.
    """
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id
