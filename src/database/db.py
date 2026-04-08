import sqlite3
import os

# Path to the local SQLite database file.
DB_PATH = "db/churn.db"

def get_connection():
    """Create the database directory if needed and return a SQLite connection."""
    os.makedirs("db", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_table():
    """Create the churn_results table if it does not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS churn_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customerID TEXT,
        risk REAL,
        strategy TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def insert_result(customerID, risk, strategy, email):
    """Insert a new churn prediction and retention recommendation record."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO churn_results (customerID, risk, strategy, email)
    VALUES (?, ?, ?, ?)
    """, (customerID, risk, strategy, email))

    conn.commit()
    conn.close()


def get_history():
    """Fetch all saved churn results ordered by newest first."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM churn_results ORDER BY created_at DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows