import sqlite3
import json
import os
from datetime import datetime

# Define the path for the database file
DB_PATH = "./data/orchestrator_logs.db"

def init_db():
    """
    Initializes the SQLite database. Creates the tracking table if it doesn't exist.
    """
    os.makedirs("./data", exist_ok=True)
    
    # Connect to SQLite (this creates the file if it doesn't exist)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Create the execution_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_command TEXT NOT NULL,
                generated_schema TEXT,
                execution_status TEXT NOT NULL
            )
        ''')
        conn.commit()
    print("SQLite Database initialized at /data/orchestrator_logs.db")

def log_execution(user_command: str, schema: dict, status: str):
    """
    Inserts a new operational log into the database for traceability.
    """
    # Convert the JSON schema dictionary into a string for storage
    schema_str = json.dumps(schema, indent=2) if schema else "No schema generated"
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO execution_logs (user_command, generated_schema, execution_status)
            VALUES (?, ?, ?)
        ''', (user_command, schema_str, status))
        conn.commit()
        
def get_recent_logs(limit=10):
    """
    Retrieves the most recent logs (useful if you want to show them in the UI later).
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row # Returns dictionaries instead of tuples
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, user_command, execution_status 
            FROM execution_logs 
            ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]