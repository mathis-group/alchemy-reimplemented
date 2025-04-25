import sqlite3
import pandas as pd

db_name = '/Users/jjoseph/Desktop/Projects/AICHEMY_VISUALISER/database/alchemy_data.db'

def check_database():
    try:
        # Connect to the database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Check if tables are present
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'experiment_%'")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("ERROR: No tables found in the database.")
            return

        print(f"Found tables: {tables}")

        first_table = tables[0]
        query = f"SELECT * FROM {first_table}"
        df = pd.read_sql_query(query, conn)

        print(f"Data from {first_table}:\n{df.head()}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

# Run the check
check_database()
