"""
run_database_setup.py — Executes the SQL setup script using SQLite

Unlike the original project which required MySQL to be installed,
our version uses SQLite which comes built into Python. No extra setup needed!

Usage:
  python3 database/run_database_setup.py
"""

import sqlite3
import os


def run_setup():
    # Figure out file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(script_dir, "database_setup.sql")
    db_path = os.path.join(script_dir, "..", "momo_tracker.db")

    print("\n--- MoMo Transaction Tracker — Database Setup ---")
    print(f"SQL script: {sql_path}")
    print(f"Database:   {db_path}")

    # Check if the SQL file exists
    if not os.path.exists(sql_path):
        print(f"\n Error: Could not find '{sql_path}'")
        return

    # Read the SQL script
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    # Connect to SQLite (creates the file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Execute the entire script
        cursor.executescript(sql_script)
        conn.commit()
        print("\n Tables created successfully!")

        # Verify — list all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        print(f"\n Tables in database ({len(tables)}):")
        for table in tables:
            # Count rows in each table
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {table[0]:<25} ({count} rows)")

        # Quick test query — show a sample transaction with JOINs
        print("\n Sample query — Latest 3 transactions:")
        cursor.execute("""
            SELECT 
                t.tx_ref,
                s.full_name AS sender,
                r.full_name AS receiver,
                c.name AS category,
                t.amount,
                t.timestamp
            FROM transactions t
            JOIN users s ON t.sender_id = s.user_id
            JOIN users r ON t.receiver_id = r.user_id
            JOIN categories c ON t.category_id = c.category_id
            ORDER BY t.timestamp DESC
            LIMIT 3
        """)

        rows = cursor.fetchall()
        print(f"   {'Ref':<20} {'Sender':<22} {'Receiver':<22} {'Category':<20} {'Amount':>12} {'Date'}")
        print(f"   {'-'*20} {'-'*22} {'-'*22} {'-'*20} {'-'*12} {'-'*19}")
        for row in rows:
            print(f"   {row[0]:<20} {row[1]:<22} {row[2]:<22} {row[3]:<20} {row[4]:>12,.2f} {row[5]}")

        print(f"\n Database setup complete! File saved at: {db_path}\n")

    except Exception as e:
        print(f"\n Error during setup: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    run_setup()
