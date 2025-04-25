import sqlite3
from alchemy import PySoup, PyReactor

def setup_database(db_name='alchemy_data.db'):
    conn = sqlite3.connect(db_name)
    conn.close()

def create_experiment_table(db_name, table_name):
    conn = sqlite3.connect(db_name)
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
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    experiment_ids = [int(name[0].split('_')[1]) for name in tables if name[0].startswith('experiment_')]
    next_experiment_id = (max(experiment_ids) if experiment_ids else 0) + 1

    conn.close()
    return next_experiment_id

def insert_data(db_name, table_name, series_number, lambda_expressions):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    for expr in lambda_expressions:
        cursor.execute(f'''
        INSERT INTO {table_name} (series_number, lambda_expression)
        VALUES (?, ?)
        ''', (series_number, expr))

    conn.commit()
    conn.close()

def fetch_data_from_table(db_name, table_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    conn.close()
    return rows

def run_simulation_and_store():
    soup = PySoup()
    reactor = PyReactor()
    soup = PySoup.from_config(reactor)

    soup.set_limit(100)
    expressions = ["\\x.x", "\\x.\\y.x", "\\x.\\y.\\z.x z (y z)"]
    soup.perturb(expressions)

    steps_run = soup.simulate_for(100, log=False)
    final_expressions = soup.expressions()

    print(f"Simulation ran for {steps_run} steps")
    print("Final expressions:", final_expressions)

    db_name = 'alchemy_data.db'
    setup_database(db_name)  #  database is set up

    experiment_id = get_next_experiment_id(db_name)
    table_name = generate_table_name(experiment_id)
    create_experiment_table(db_name, table_name)

    insert_data(db_name, table_name, series_number=1, lambda_expressions=final_expressions)

    stored_data = fetch_data_from_table(db_name, table_name)
    print(f"Stored data in {table_name}:")
    for row in stored_data:
        print(row)

# Run the simulation and store the results
if __name__ == "__main__":
    run_simulation_and_store()
