"""
db.py
-------
Handles the MySQL database connection for the
Smart Career Recommendation System (Phase 1).
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "smart_career_system"),
    "port": int(os.getenv("DB_PORT", 3306)),
}


def get_db_connection():
    """
    Creates and returns a new MySQL database connection.
    Returns None if the connection fails.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"[DB ERROR] Could not connect to MySQL: {e}")
        return None


def test_connection():
    """
    Utility function to quickly test if the DB connection works.
    Run this file directly to test: python db.py
    """
    conn = get_db_connection()
    if conn and conn.is_connected():
        print("✅ Successfully connected to MySQL database.")
        conn.close()
    else:
        print("❌ Failed to connect to MySQL database.")


if __name__ == "__main__":
    test_connection()
