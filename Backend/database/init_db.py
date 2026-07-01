import sqlite3
import os

# Get the directory where this script resides
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to this directory
DB_PATH = os.path.join(BASE_DIR, 'verte.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')

def initialize_database():
    if not os.path.exists(SCHEMA_PATH):
        print(f"❌ Error: Schema file '{SCHEMA_PATH}' not found.")
        return

    try:
        # Connect to (or create) the database file
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Enable Foreign Key support for this connection
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            with open(SCHEMA_PATH, "r") as f:
                schema_sql = f.read()
            
            # executescript allows multiple SQL commands (creating multiple tables)
            conn.executescript(schema_sql)
            
            print(f"✅ Database initialized successfully at: {DB_PATH}")
            
    except sqlite3.Error as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    print("🗄️ Setting up Verte database...")
    initialize_database()