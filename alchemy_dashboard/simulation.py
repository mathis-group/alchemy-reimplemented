# alchemy_dashboard/simulation.py

import os
import alchemy
import random
from collections import Counter
from models import (
    save_configuration, 
    save_experiment_state, 
    save_averages, 
    get_last_config_id
)

def load_input_expressions(generator_type, gen_params):
    """
    Load initial expressions based on generator type and parameters.
    
    Args:
        generator_type (str): Type of generator to use
        gen_params (dict): Generator parameters
    
    Returns:
        list: List of initial expressions
    """
    if generator_type == "from_file":
        filename = gen_params.get("filename")
        if filename and os.path.exists(filename):
            with open(filename, "r") as f:
                return [line.strip() for line in f if line.strip()]
        return []
    
    elif generator_type == "BTree":
        size = gen_params.get("size", 5)
        fvp = gen_params.get("freevar_generation_probability", 0.5)
        max_fv = gen_params.get("max_free_vars", 3)
        std_type = gen_params.get("standardization", "prefix")
        num_expr = gen_params.get("num_expressions", 10)
        
        btree_gen = alchemy.PyBTreeGen.from_config(
            size, fvp, max_fv, alchemy.PyStandardization(std_type)
        )
        return btree_gen.generate_n(num_expr)
    
    elif generator_type == "Fontana":
        # Implement Fontana generator if available
        # This is a placeholder - implement based on your alchemy library
        return ["(λx.x)", "(λx.λy.x y)", "(λx.x x)"]
    
    else:
        # Default to some basic lambda expressions
        return ["(λx.x)", "(λy.y)", "(λz.z)"]


# Update run_experiment function to handle experiment naming
def run_experiment(config):
    """
    Run an alchemy experiment and save results directly to the database.
    
    Args:
        config (dict): Configuration dictionary with experiment parameters
        
    Returns:
        dict: Dictionary containing experiment results and metadata
    """
    # Extract configuration parameters
    generator_type = config["input_expressions"]["generator"]
    gen_params = config["input_expressions"].get("params", {})
    total_collisions = config.get("total_collisions", 1000)
    polling_frequency = config.get("polling_frequency", 10)
    
    # Get experiment name if provided
    experiment_name = config.get("name")
    
    # Generate random seed if not provided
    random_seed = config.get("random_seed", random.randint(1, 1000000))
    
    # Extract probability ranges and freevar generation probability
    probability_range = None
    freevar_generation_probability = None
    
    if generator_type == "Fontana" and "params" in config["input_expressions"]:
        params = config["input_expressions"]["params"]
        if "abs_range" in params and "app_range" in params:
            probability_range = json.dumps({
                "abs_range": params["abs_range"],
                "app_range": params["app_range"]
            })
    
    if generator_type == "BTree" and "params" in config["input_expressions"]:
        params = config["input_expressions"]["params"]
        if "freevar_generation_probability" in params:
            freevar_generation_probability = params["freevar_generation_probability"]
    
    # Save configuration to database
    config_id = save_configuration(
        random_seed,
        generator_type, 
        total_collisions,
        polling_frequency,
        probability_range,
        freevar_generation_probability,
        experiment_name
    )
    
    # Initialize alchemy simulation
    soup = alchemy.PySoup()
    expressions = load_input_expressions(generator_type, gen_params)
    
    # Set up the simulation
    soup.perturb(expressions)
    collision_count = 0
    
    # Save initial state (collision 0)
    initial_state = soup.expressions()
    initial_expr_counter = Counter(initial_state)
    
    # Save each initial expression with its count
    for expr, count in initial_expr_counter.items():
        save_experiment_state(config_id, 0, expr, count)
    
    # Also save initial metrics
    initial_entropy = soup.population_entropy()
    initial_unique = len(set(initial_state))
    save_averages(config_id, 0, initial_entropy, initial_unique)
    
    # Run the simulation
    results = {
        'config_id': config_id,
        'collision_data': []
    }
    
    while collision_count < total_collisions:
        soup.simulate_for(1, log=False)
        collision_count += 1
        
        if (collision_count % polling_frequency == 0) or (collision_count == total_collisions):
            # Collect data for this collision
            state = soup.expressions()
            expr_counter = Counter(state)
            
            # Calculate metrics
            entropy = soup.population_entropy()
            unique_count = len(set(state))
            
            # Save each expression with its count
            for expr, count in expr_counter.items():
                save_experiment_state(config_id, collision_count, expr, count)
            
            # Save metrics to the Averages table
            save_averages(config_id, collision_count, entropy, unique_count)
            
            # Store data for result return value
            results['collision_data'].append({
                'collision_number': collision_count,
                'entropy': entropy,
                'unique_expressions': unique_count
            })
    
    return results