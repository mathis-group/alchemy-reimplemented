import os
import sqlite3
from alchemy import PySoup, PyReactor

def get_db_path(db_name='alchemy_data.db'):
    # Absolute path to the database
    db_dir = '/Users/jjoseph/Desktop/Projects/AICHEMY_VISUALISER/database'
    return os.path.join(db_dir, db_name)

def setup_database(db_name='alchemy_data.db'):
    conn = sqlite3.connect(get_db_path(db_name))
    conn.close()

def create_experiment_table(db_name, table_name):
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()

    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_number INTEGER NOT NULL,
        lambda_expression TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def generate_table_name(experiment_id):
    return f"experiment_{experiment_id}"

def get_next_experiment_id(db_name='alchemy_data.db'):
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    experiment_ids = [int(name[0].split('_')[1]) for name in tables if name[0].startswith('experiment_')]
    next_experiment_id = (max(experiment_ids) if experiment_ids else 0) + 1

    conn.close()
    return next_experiment_id

def insert_data(db_name, table_name, series_number, lambda_expressions):
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()

    for expr in lambda_expressions:
        cursor.execute(f'''
        INSERT INTO {table_name} (series_number, lambda_expression)
        VALUES (?, ?)
        ''', (series_number, expr))

    conn.commit()
    conn.close()

def run_soup_and_store():
    # Initialize soup and reactor
    soup = PySoup()
    reactor = PyReactor()
    soup = PySoup.from_config(reactor)

    
    soup.set_limit(100)
    expressions = ["\\x.x", "\\x.\\y.x", "\\x.\\y.\\z.x z (y z)"]
    soup.perturb(expressions)

    # Run the simulation
    steps_run = soup.simulate_for(10000, log=False)
    final_expressions = soup.expressions()

    print(f"Simulation ran for {steps_run} steps")
    print("Final expressions:", final_expressions)

    #  Store results in the database 
    db_name = 'alchemy_data.db'
    setup_database(db_name)  

    
    experiment_id = get_next_experiment_id(db_name)
    table_name = generate_table_name(experiment_id)
    create_experiment_table(db_name, table_name)

    
    insert_data(db_name, table_name, series_number=1, lambda_expressions=final_expressions)

    
    print(f"Stored data in {table_name}:")
    for row in fetch_data_from_table(db_name, table_name):
        print(row)

def fetch_data_from_table(db_name, table_name):
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_tables_sorted(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    # Extract numbers from table names and sort them numerically
    sorted_tables = sorted(tables, key=lambda x: int(re.search(r'\d+', x[0]).group()))

    conn.close()
    return [table[0] for table in sorted_tables]


if __name__ == "__main__":
    run_soup_and_store()
