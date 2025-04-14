# alchemy_dashboard/db_utils.py

import os
import sqlite3
import json
import pandas as pd
from config import DB_NAME


def check_database_exists(db_path=DB_NAME):
    """Check if the database file exists."""
    return os.path.exists(db_path)



# Update get_experiment_configs function to include the name field
def get_experiment_configs(db_path=DB_NAME):
    """Fetch all experiment configurations from the database."""
    if not check_database_exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            config_id, 
            random_seed,
            generator_type, 
            total_collisions, 
            polling_frequency, 
            timestamp,
            name
        FROM Configurations 
        ORDER BY timestamp DESC
    """)
    configs = cursor.fetchall()
    conn.close()
    return configs
# Update get_experiment_details to include the name field
def get_experiment_details(config_id, db_path=DB_NAME):
    """Get detailed information about a specific experiment."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get configuration details
    cursor.execute("""
        SELECT 
            config_id, 
            random_seed,
            generator_type, 
            total_collisions, 
            polling_frequency, 
            probability_range,
            freevar_generation_probability,
            timestamp,
            name
        FROM Configurations 
        WHERE config_id = ?
    """, (config_id,))
    config = cursor.fetchone()
    
    if not config:
        conn.close()
        return None, None, None

    # Get the initial expressions (collision 0)
    cursor.execute("""
        SELECT expression, count
        FROM Experiment
        WHERE config_id = ? AND collision_number = 0
    """, (config_id,))
    initial_expressions = cursor.fetchall()

    # Get metrics data for all collisions
    cursor.execute("""
        SELECT 
            collision_number, 
            entropy, 
            unique_expressions
        FROM Averages
        WHERE config_id = ?
        ORDER BY collision_number
    """, (config_id,))
    metrics = cursor.fetchall()

    conn.close()
    return config, metrics, initial_expressions

import pandas as pd
from config import DB_NAME


import sqlite3
import pandas as pd
from config import DB_NAME

def query_df_by_config_id(config_id):
    """
    Query Averages table for a config_id and return pandas DataFrame.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT collision_number, entropy, unique_expressions
        FROM Averages
        WHERE config_id = ?
        ORDER BY collision_number
    ''', (config_id,))
    
    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["collision_num", "entropy", "len_unique_expressions"])
    return df


def process_collision_data(metrics):
    """Process collision metrics data into a DataFrame for plotting."""
    data = []
    for metric in metrics:
        collision_number, entropy, unique_expressions = metric
        data.append({
            'collision_number': collision_number,
            'entropy': entropy,
            'unique_expressions_count': unique_expressions
        })
    return pd.DataFrame(data)


def get_expressions_for_collision(config_id, collision_number, db_path=DB_NAME):
    """
    Get all expressions for a specific collision.
    If collision_number is -1, returns the last collision.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if collision_number == -1:
        # Get the highest collision number for this config
        cursor.execute("""
            SELECT MAX(collision_number)
            FROM Experiment
            WHERE config_id = ?
        """, (config_id,))
        result = cursor.fetchone()
        if result and result[0] is not None:
            collision_number = result[0]
        else:
            conn.close()
            return []

    cursor.execute("""
        SELECT expression, count
        FROM Experiment
        WHERE config_id = ? AND collision_number = ?
        ORDER BY count DESC
    """, (config_id, collision_number))
    
    expressions = cursor.fetchall()
    conn.close()
    
    return expressions


def get_experiment_metrics(config_ids, metric_name, db_path=DB_NAME):
    """
    Get specific metric data for multiple experiments for comparison.
    
    Args:
        config_ids (list): List of configuration IDs to compare
        metric_name (str): Name of the metric to retrieve ('entropy' or 'unique_expressions')
        
    Returns:
        dict: Dictionary mapping config_id to DataFrame with collision_number and metric value
    """
    if not config_ids:
        return {}
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    result = {}
    for config_id in config_ids:
        cursor.execute("""
            SELECT generator_type, random_seed
            FROM Configurations
            WHERE config_id = ?
        """, (config_id,))
        config_info = cursor.fetchone()
        
        if not config_info:
            continue
            
        generator_type, random_seed = config_info
        
        # Get the metric data
        cursor.execute(f"""
            SELECT 
                collision_number, 
                {metric_name}
            FROM Averages
            WHERE config_id = ?
            ORDER BY collision_number
        """, (config_id,))
        
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['collision_number', metric_name])
        
        result[config_id] = {
            'data': df,
            'generator_type': generator_type,
            'random_seed': random_seed
        }
    
    conn.close()
    return result
import sqlite3
from config import DB_NAME
import json

# Update get_experiment_details_and_expressions to include the name field
def get_experiment_details_and_expressions(config_id):
    """
    Return metadata + initial expressions for a given experiment config.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get config row
    cursor.execute('''
        SELECT *
        FROM Configurations
        WHERE config_id = ?
    ''', (config_id,))
    config = cursor.fetchone()

    if not config:
        conn.close()
        raise ValueError(f"No configuration found with ID {config_id}")

    # Format generator params (stored as JSON text in your column)
    if config["probability_range"]:
        try:
            generator_params = json.loads(config["probability_range"])
        except json.JSONDecodeError:
            generator_params = {}
    else:
        generator_params = {}

    # Get expressions from first collision
    cursor.execute('''
        SELECT expression
        FROM Experiment
        WHERE config_id = ? AND collision_number = 0
        ORDER BY count DESC
    ''', (config_id,))
    expressions = [row["expression"] for row in cursor.fetchall()]

    conn.close()

    return {
        "generator": config["generator_type"],
        "total_collisions": config["total_collisions"],
        "polling_frequency": config["polling_frequency"],
        "timestamp": config["timestamp"],
        "generator_params": generator_params,
        "name": config["name"]
    }, expressions


def import_json_to_db(json_path, db_path=DB_NAME):
    """
    Import experiment data from a JSON file into the database.
    
    Args:
        json_path (str): Path to the JSON file
        db_path (str): Path to the database file
        
    Returns:
        int: The ID of the newly created configuration
    """
    from models import save_configuration, save_experiment_state, save_averages
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Extract configuration
        config_data = data.get("config", {})
        generator_type = config_data.get("input_expressions", {}).get("generator", "unknown")
        total_collisions = config_data.get("total_collisions", 1000)
        polling_frequency = config_data.get("polling_frequency", 10)
        
        # Extract generator-specific params
        generator_params = config_data.get("input_expressions", {}).get("params", {})
        
        # Prepare data for database
        probability_range = None
        freevar_probability = None
        
        if generator_type == "Fontana" and "abs_range" in generator_params and "app_range" in generator_params:
            probability_range = json.dumps({
                "abs_range": generator_params["abs_range"],
                "app_range": generator_params["app_range"]
            })
        
        if generator_type == "BTree" and "freevar_generation_probability" in generator_params:
            freevar_probability = generator_params["freevar_generation_probability"]
        
        # Generate random seed if not present
        random_seed = config_data.get("random_seed", 12345)
        
        # Save configuration to database
        config_id = save_configuration(
            random_seed,
            generator_type,
            total_collisions,
            polling_frequency,
            probability_range,
            freevar_probability
        )
        
        # Process collision data
        collisions_data = data.get("collisions_data", {})
        
        for key, collision in collisions_data.items():
            collision_number = int(key.split("_")[1]) if "_" in key else 0
            state = collision.get("state", [])
            entropy = collision.get("entropy", 0)
            unique_expressions = len(collision.get("unique_expressions", [])) if "unique_expressions" in collision else 0
            
            # Count expressions
            from collections import Counter
            expr_counter = Counter(state)
            
            # Save each expression with its count
            for expr, count in expr_counter.items():
                save_experiment_state(config_id, collision_number, expr, count)
            
            # Save metrics
            save_averages(config_id, collision_number, entropy, unique_expressions)
        
        return config_id
        
    except Exception as e:
        print(f"Error importing JSON to database: {e}")
        return None
    

def get_entropy_and_histogram(config_id, collision_number):
    """
    Fetch entropy and histogram (expression + count) for a specific collision.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get entropy value
    cursor.execute('''
        SELECT entropy
        FROM Averages
        WHERE config_id = ? AND collision_number = ?
    ''', (config_id, collision_number))
    row = cursor.fetchone()
    entropy = row[0] if row else None

    # Get histogram (expression counts)
    cursor.execute('''
        SELECT expression, count
        FROM Experiment
        WHERE config_id = ? AND collision_number = ?
        ORDER BY count DESC
    ''', (config_id, collision_number))
    rows = cursor.fetchall()
    conn.close()

    histogram = [{"expression": expr, "count": cnt} for expr, cnt in rows]

    return {
        "entropy": entropy,
        "histogram": histogram
    }