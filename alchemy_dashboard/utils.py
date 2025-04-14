# # alchemy_dashboard/utils.py

# import json
# import base64
# import pandas as pd
# from plotting import create_styled_figure  

# def parse_uploaded_json(file_content):
#     """
#     Decode and parse base64-encoded uploaded JSON file content.
    
#     Parameters:
#         file_content (str): Base64 string from FileInput
    
#     Returns:
#         dict or None: Parsed JSON dictionary if successful, otherwise None
#     """
#     try:
#         decoded = base64.b64decode(file_content).decode('utf-8')
#         return json.loads(decoded)
#     except Exception as e:
#         print(f"[utils] Error parsing uploaded JSON: {e}")
#         return None


# def extract_data_from_json(json_data):
#     """
#     Extract experiment metadata and collision data from uploaded JSON structure.
    
#     Parameters:
#         json_data (dict): Parsed JSON dict from user-uploaded file
    
#     Returns:
#         dict: {
#             'metadata': {...},
#             'processed_data': pd.DataFrame
#         } or None if parsing fails
#     """
#     if not json_data:
#         return None

#     config = json_data.get('config', {})
#     collisions_data = json_data.get('collisions_data', {})

#     metadata = {
#         'total_collisions': config.get('total_collisons', 0),  # typo in original key: "total_collisons"
#         'polling_frequency': config.get('polling_frequency', 0),
#         'generator_type': config.get('input_expressions', {}).get('generator', 'unknown'),
#         'generator_params': config.get('input_expressions', {}).get('params', {}),
#         'measurements': config.get('measurements', [])
#     }

#     processed_data = []
#     for key, value in collisions_data.items():
#         collision_number = int(key.split('_')[1]) if '_' in key else 0
#         entropy = value.get('entropy', 0)
#         unique_expressions = value.get('unique_expressions', [])
#         state = value.get('state', [])
        
#         processed_data.append({
#             'collision_number': collision_number,
#             'entropy': entropy,
#             'unique_expressions_count': len(unique_expressions),
#             'total_expressions': len(state)
#         })

#     return {
#         'metadata': metadata,
#         'processed_data': pd.DataFrame(processed_data)
#     }

# alchemy_dashboard/utils.py

import json
import base64
import pandas as pd
from plotting import create_styled_figure  

def parse_uploaded_json(file_content):
    """
    Decode and parse base64-encoded uploaded JSON file content.
    
    Parameters:
        file_content (str): Base64 string from FileInput
    
    Returns:
        dict or None: Parsed JSON dictionary if successful, otherwise None
    """
    try:
        decoded = base64.b64decode(file_content).decode('utf-8')
        return json.loads(decoded)
    except Exception as e:
        print(f"[utils] Error parsing uploaded JSON: {e}")
        return None


def extract_data_from_json(json_data):
    """
    Extract experiment metadata and collision data from uploaded JSON structure.
    
    Parameters:
        json_data (dict): Parsed JSON dict from user-uploaded file
    
    Returns:
        dict: {
            'metadata': {...},
            'processed_data': pd.DataFrame
        } or None if parsing fails
    """
    if not json_data:
        return None

    config = json_data.get('config', {})
    collisions_data = json_data.get('collisions_data', {})

    metadata = {
        'total_collisions': config.get('total_collisons', 0),  # typo in original key: "total_collisons"
        'polling_frequency': config.get('polling_frequency', 0),
        'generator_type': config.get('input_expressions', {}).get('generator', 'unknown'),
        'generator_params': config.get('input_expressions', {}).get('params', {}),
        'measurements': config.get('measurements', [])
    }

    processed_data = []
    for key, value in collisions_data.items():
        collision_number = int(key.split('_')[1]) if '_' in key else 0
        entropy = value.get('entropy', 0)
        unique_expressions = value.get('unique_expressions', [])
        state = value.get('state', [])
        
        processed_data.append({
            'collision_number': collision_number,
            'entropy': entropy,
            'unique_expressions_count': len(unique_expressions),
            'total_expressions': len(state)
        })

    return {
        'metadata': metadata,
        'processed_data': pd.DataFrame(processed_data)
    }



import json

def load_results(filename):
    with open(filename, "r") as f:
        return json.load(f)
