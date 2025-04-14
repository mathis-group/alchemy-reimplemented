# alchemy_dashboard/models.py

import sqlite3
import json
import os
from datetime import datetime
from config import DB_NAME

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, create_engine

def init_database():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create Configurations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Configurations (
        config_id INTEGER PRIMARY KEY AUTOINCREMENT,
        random_seed INTEGER,
        generator_type TEXT NOT NULL,
        total_collisions INTEGER NOT NULL,
        polling_frequency INTEGER NOT NULL,
        probability_range TEXT,
        freevar_generation_probability REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        name TEXT
    )
    ''')
    
    # Check if name column exists, add it if it doesn't
    # This handles existing databases that were created before the name column was added
    try:
        cursor.execute("SELECT name FROM pragma_table_info('Configurations') WHERE name='name'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Configurations ADD COLUMN name TEXT")
            cursor.execute("UPDATE Configurations SET name = 'Experiment ' || config_id WHERE name IS NULL")
    except Exception as e:
        print(f"Error adding name column: {e}")
    
    # Create Experiment table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Experiment (
        experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_id INTEGER,
        collision_number INTEGER NOT NULL,
        expression TEXT NOT NULL,
        count INTEGER NOT NULL,
        FOREIGN KEY (config_id) REFERENCES Configurations(config_id)
    )
    ''')
    
    # Create Averages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Averages (
        average_id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_id INTEGER,
        collision_number INTEGER NOT NULL,
        entropy REAL,
        unique_expressions INTEGER,
        FOREIGN KEY (config_id) REFERENCES Configurations(config_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
# Update the save_configuration function to accept a name parameter

def save_configuration(random_seed, generator_type, total_collisions, polling_frequency, 
                      probability_range=None, freevar_generation_probability=None, name=None):
    """
    Save experiment configuration to the database.
    
    Args:
        random_seed (int): Random seed for reproducibility
        generator_type (str): Type of generator used (e.g., "Fontana")
        total_collisions (int): Total number of collisions to run
        polling_frequency (int): Frequency at which data is collected
        probability_range (str): JSON representation of probability ranges
        freevar_generation_probability (float): Probability of generating free variables
        name (str): User-specified name for the experiment (optional)
    
    Returns:
        int: The ID of the newly created configuration
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # If name is not provided, create a default one that will be updated after we know the ID
    default_name = name or "Unnamed Experiment"
    
    cursor.execute('''
    INSERT INTO Configurations 
    (random_seed, generator_type, total_collisions, polling_frequency, 
     probability_range, freevar_generation_probability, name)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        random_seed,
        generator_type,
        total_collisions,
        polling_frequency,
        probability_range,
        freevar_generation_probability,
        default_name
    ))
    
    config_id = cursor.lastrowid
    
    # If no name was provided, update with a default name that includes the ID
    if name is None:
        cursor.execute('''
        UPDATE Configurations
        SET name = ? 
        WHERE config_id = ?
        ''', (f"Experiment {config_id}", config_id))
    
    conn.commit()
    conn.close()
    
    return config_id


# Add a function to update experiment name
def update_experiment_name(config_id, new_name):
    """
    Update the name of an existing experiment.
    
    Args:
        config_id (int): ID of the experiment to update
        new_name (str): New name for the experiment
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        UPDATE Configurations
        SET name = ?
        WHERE config_id = ?
        ''', (new_name, config_id))
        
        conn.commit()
        success = cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating experiment name: {e}")
        conn.rollback()
        success = False
    
    conn.close()
    return success

def save_experiment_state(config_id, collision_number, expression, count):
    """
    Save experiment state to the database.
    
    Args:
        config_id (int): ID of the configuration
        collision_number (int): Current collision number
        expression (str): The lambda expression
        count (int): Count/frequency of this expression
    
    Returns:
        int: The ID of the newly created experiment state entry
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO Experiment 
    (config_id, collision_number, expression, count)
    VALUES (?, ?, ?, ?)
    ''', (
        config_id,
        collision_number,
        expression,
        count
    ))
    
    experiment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return experiment_id

def save_averages(config_id, collision_number, entropy, unique_expressions):
    """
    Save averages/metrics to the database.
    
    Args:
        config_id (int): ID of the configuration
        collision_number (int): Collision number
        entropy (float): Entropy value
        unique_expressions (int): Count of unique expressions
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO Averages 
    (config_id, collision_number, entropy, unique_expressions)
    VALUES (?, ?, ?, ?)
    ''', (
        config_id,
        collision_number,
        entropy,
        unique_expressions
    ))
    
    conn.commit()
    conn.close()

def get_last_config_id():
    """Get the ID of the most recently added configuration."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(config_id) FROM Configurations")
    last_id = cursor.fetchone()[0]
    
    conn.close()
    return last_id if last_id else 1  # Default to 1 if no configurations exist

def get_experiment_configs():
    """Get all experiment configurations."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT config_id, random_seed, generator_type, total_collisions, polling_frequency, timestamp
    FROM Configurations
    ORDER BY timestamp DESC
    ''')
    
    configs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return configs

def get_experiment_data(config_id):
    """Get experiment data for a specific configuration."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get configuration details
    cursor.execute('''
    SELECT * FROM Configurations WHERE config_id = ?
    ''', (config_id,))
    config = dict(cursor.fetchone())
    
    # Get averages data
    cursor.execute('''
    SELECT collision_number, entropy, unique_expressions
    FROM Averages
    WHERE config_id = ?
    ORDER BY collision_number
    ''', (config_id,))
    averages = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'config': config,
        'averages': averages
    }

def get_experiment_expressions(config_id, collision_number):
    """Get expressions for a specific configuration and collision number."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT expression, count
    FROM Experiment
    WHERE config_id = ? AND collision_number = ?
    ORDER BY count DESC
    ''', (config_id, collision_number))
    
    expressions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return expressions

# If not already present:
from sqlalchemy.orm import sessionmaker

# This should already exist:
engine = create_engine("sqlite:///alchemy_experiments.db", echo=False)

# Add this:
Session = sessionmaker(bind=engine)
db_session = Session()

__all__ = ["Base", "ExperimentConfiguration", "ExperimentResult", "db_session"]
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

