import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from bokeh.resources import CDN
from simulation import run_experiment
from visualization import get_simulation_components
from models import init_database, save_configuration, save_experiment_state, save_averages, get_experiment_configs
from db_utils import (
    get_experiment_details, 
    process_collision_data,
    get_experiment_metrics,
    get_expressions_for_collision
)
from plotting import create_bokeh_plots_from_metrics
import re

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploaded_configs'
app.config['EXPERIMENT_FOLDER'] = 'experiments'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['EXPERIMENT_FOLDER'], exist_ok=True)

# Initialize database on startup
init_database()

latest_json_path = None

@app.route('/')
def index():
    global latest_json_path
    if latest_json_path is not None:
        try:
            script, div = get_simulation_components(latest_json_path)
        except Exception as e:
            print("Error rendering Bokeh components:", e)
            script, div = "", ""
    else:
        script, div = "", ""
    return render_template('index_with_bokeh.html', bokeh_script=script, bokeh_div=div)

# Update the run_simulation_form route to handle experiment names
@app.route('/run_simulation_form', methods=['POST'])
def run_simulation_form():
    try:
        # Extract form data
        generator_type = request.form.get('generator_type', 'Fontana')
        total_collisions = int(request.form.get('total_collisions', 1000))
        polling_frequency = int(request.form.get('polling_frequency', 10))
        random_seed = int(request.form.get('random_seed', 42))
        experiment_name = request.form.get('experiment_name', '')
        
        # Build configuration based on generator type
        config = {
            "random_seed": random_seed,
            "total_collisions": total_collisions,
            "polling_frequency": polling_frequency,
            "name": experiment_name if experiment_name else None,
            "input_expressions": {
                "generator": generator_type,
                "params": {}
            }
        }
        
        # Add generator-specific parameters
        if generator_type == "BTree":
            config["input_expressions"]["params"] = {
                "size": int(request.form.get('btree_size', 5)),
                "freevar_generation_probability": float(request.form.get('freevar_probability', 0.5)),
                "max_free_vars": int(request.form.get('max_free_vars', 3)),
                "standardization": request.form.get('standardization', 'prefix'),
                "num_expressions": int(request.form.get('num_expressions', 10))
            }
        elif generator_type == "Fontana":
            config["input_expressions"]["params"] = {
                "abs_range": [
                    float(request.form.get('abs_low', 0.1)),
                    float(request.form.get('abs_high', 0.5))
                ],
                "app_range": [
                    float(request.form.get('app_low', 0.2)),
                    float(request.form.get('app_high', 0.6))
                ],
                "max_depth": int(request.form.get('max_depth', 5)),
                "max_free_vars": int(request.form.get('fontana_max_fv', 2))
            }
        elif generator_type == "from_file":
            # For file-based input, check if a file was uploaded
            if 'expressions_file' in request.files and request.files['expressions_file'].filename:
                file = request.files['expressions_file']
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                config["input_expressions"]["params"] = {"filename": file_path}
            else:
                # Use direct input if provided
                direct_input = request.form.get('direct_input', '')
                if direct_input.strip():
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"direct_input_{random_seed}.txt")
                    with open(temp_path, 'w') as f:
                        f.write(direct_input)
                    config["input_expressions"]["params"] = {"filename": temp_path}
                else:
                    return jsonify({
                        "status": "error",
                        "message": "No expressions provided for 'from_file' generator"
                    })
        
        # Run the experiment with parsed config
        result = run_experiment(config)
        
        # Get experiment details for charts
        config_id = result['config_id']
        config_details, metrics, initial_expressions = get_experiment_details(config_id)
        
        if metrics:
            df = process_collision_data(metrics)
            
            # Generate charts
            from bokeh.embed import components
            from plotting import plot_experiment_metrics
            
            plots = plot_experiment_metrics(df)
            
            if len(plots) >= 2:
                # Create separate components for each plot
                entropy_script, entropy_div = components(plots[0])
                unique_script, unique_div = components(plots[1])
                
                # Combine scripts for template compatibility
                bokeh_script = entropy_script + unique_script
            else:
                bokeh_script, entropy_div, unique_div = "", "", ""
        else:
            bokeh_script, entropy_div, unique_div = "", "", ""
        
        response = {
            "status": "success",
            "config_id": config_id,
            "experiment_name": config_details[8] if len(config_details) > 8 else f"Experiment {config_id}",
            "initial_expressions": len(initial_expressions) if initial_expressions else 0,
            "charts": {
                "entropy_div": entropy_div,
                "unique_div": unique_div,
                "script": bokeh_script
            }
        }
        return jsonify(response)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@app.route('/debug_db')
def debug_db():
    try:
        import sqlite3
        from config import DB_NAME
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Configurations")
        configs = cursor.fetchall()
        conn.close()
        return jsonify({
            "status": "success",
            "message": f"Found {len(configs)} configurations",
            "data": configs
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

# Update view_experiment route to include experiment name
@app.route('/view_experiment/<int:config_id>')
def view_experiment(config_id):
    """View a single experiment's details and visualizations."""
    config, metrics, initial_expressions = get_experiment_details(config_id)
    
    if not config:
        return "Experiment not found", 404
    
    # Process metrics data for visualization
    df = process_collision_data(metrics)
    
    # Create plots
    from bokeh.embed import components
    from plotting import plot_experiment_metrics
    
    plots = plot_experiment_metrics(df)
    script, div = components(plots[0])  # Just get the first plot for now
    
    # Prepare context data for template
    context = {
        'config_id': config[0],
        'random_seed': config[1],
        'generator_type': config[2],
        'total_collisions': config[3],
        'polling_frequency': config[4],
        'probability_range': config[5],
        'freevar_probability': config[6],
        'timestamp': config[7],
        'name': config[8] if len(config) > 8 else f"Experiment {config[0]}",
        'initial_expressions': len(initial_expressions),
        'bokeh_script': script,
        'bokeh_div': div
    }
    
    return render_template('experiment_details.html', **context)


@app.route('/upload_json', methods=['POST'])
def upload_json():
    print("✅ upload_json route registered")
    if 'json_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded.'})
    file = request.files['json_file']
    filename = file.filename
    if not filename.endswith('.json'):
        return jsonify({'status': 'error', 'message': 'Invalid file type.'})
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    print(f"[UPLOAD] File saved to {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "collisions_data" not in data:
                return jsonify({'status': 'error', 'message': "Missing 'collisions_data' in file."})
            metrics = list(data["collisions_data"][next(iter(data["collisions_data"]))].keys())
            return jsonify({'status': 'success', 'filename': filename, 'metrics': list(metrics)})
    except json.JSONDecodeError as je:
        return jsonify({'status': 'error', 'message': f'JSON decode error: {str(je)}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/generate_visuals/<filename>', methods=['GET'])
def generate_visuals(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f"[VISUALIZE] Looking for file: {filepath}")
    if not os.path.exists(filepath):
        return jsonify({'status': 'error', 'message': f'File not found: {filepath}'})
    if os.path.getsize(filepath) == 0:
        return jsonify({'status': 'error', 'message': f'File is empty: {filepath}'})
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if "collisions_data" not in data:
            return jsonify({'status': 'error', 'message': "Missing 'collisions_data' in file."})
        from plotting import create_bokeh_from_data
        script, div = create_bokeh_from_data(data)
        return jsonify({'status': 'success', 'script': script, 'div': div})
    except json.JSONDecodeError as je:
        return jsonify({'status': 'error', 'message': f'JSON decode error: {str(je)}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Unexpected error: {str(e)}'})
    

@app.route('/continue_experiment', methods=['POST'])
def continue_experiment():
    config_id = request.form.get('config_id')
    if not config_id:
        return "No experiment selected", 400
    
    # Get the last experiment state
    last_expressions = get_expressions_for_collision(config_id, -1)  # -1 for last collision
    
    if not last_expressions:
        return "No expressions found for experiment", 400
    
    # Create a temp file with expressions
    temp_file = os.path.join(app.config['UPLOAD_FOLDER'], f"continue_exp_{config_id}.txt")
    with open(temp_file, 'w') as f:
        for expr, count in last_expressions:
            for _ in range(count):
                f.write(f"{expr}\n")
    
    # Get original config
    config_details, _, _ = get_experiment_details(config_id)
    
    # Prepare new config
    config = {
        "random_seed": config_details[1],
        "total_collisions": config_details[3],
        "polling_frequency": config_details[4],
        "input_expressions": {
            "generator": "from_file",
            "params": {"filename": temp_file}
        }
    }
    
    # Run new experiment
    result = run_experiment(config)
    
    return redirect(url_for('view_experiment', config_id=result['config_id']))
from models import update_experiment_name

# Add this route to update experiment names
@app.route('/update_experiment_name', methods=['POST'])
def update_name():
    """Update the name of an experiment."""
    try:
        config_id = int(request.form.get('config_id'))
        new_name = request.form.get('name')
        
        if not new_name or not new_name.strip():
            return jsonify({
                "status": "error",
                "message": "Name cannot be empty"
            })
            
        success = update_experiment_name(config_id, new_name)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Experiment name updated successfully"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to update experiment name"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@app.route('/perturb_and_run', methods=['POST'])
def perturb_and_run():
    return "Perturbation feature not yet implemented", 501

@app.route('/list_experiments')
def list_experiments():
    """List all experiments in the database."""
    experiments = get_experiment_configs()
    result = {'experiments': []}
    
    for exp in experiments:
        # Check if exp is a tuple/list or a dictionary
        if isinstance(exp, (list, tuple)):
            result['experiments'].append({
                'config_id': exp[0],
                'random_seed': exp[1],
                'generator_type': exp[2], 
                'total_collisions': exp[3],
                'polling_frequency': exp[4],
                'timestamp': exp[5]
            })
        elif isinstance(exp, dict):
            # If it's already a dictionary, just add it
            result['experiments'].append(exp)
    
    return jsonify(result)

@app.route('/compare_experiments', methods=['GET', 'POST'])
def compare_experiments():
    """Compare multiple experiments."""
    if request.method == 'POST':
        # Get selected experiments and metric from form
        selected_ids = request.form.getlist('experiment_ids')
        metric = request.form.get('metric', 'entropy')
        
        if not selected_ids:
            return redirect(url_for('compare_experiments'))
        
        # Convert to integers
        config_ids = [int(id) for id in selected_ids]
        
        # Get metric data for selected experiments
        metric_data = get_experiment_metrics(config_ids, metric)
        
        # Create comparison plot
        from plotting import plot_comparison_metrics
        from bokeh.embed import components
        
        comparison_plot = plot_comparison_metrics(metric_data, metric)
        script, div = components(comparison_plot)
        
        # Get all experiments for the form
        all_experiments = get_experiment_configs()
        
        return render_template(
            'compare_experiments.html',
            experiments=all_experiments,
            selected_ids=selected_ids,
            selected_metric=metric,
            bokeh_script=script,
            bokeh_div=div
        )
    else:
        # Display form to select experiments for comparison
        experiments = get_experiment_configs()
        return render_template('compare_experiments.html', experiments=experiments)

from flask import jsonify
from plotting import generate_bokeh_components  # or whatever file you use

@app.route('/get_experiment_plot/<int:config_id>')
def get_experiment_plot(config_id):
    try:
        print(f"[DEBUG] Plot request for config_id={config_id}")
        script, entropy_div, unique_div = generate_bokeh_components(config_id)
        
        # Use regex to remove any <script ...> and </script> tags
        clean_script = re.sub(r'<script[^>]*>', '', script)
        clean_script = clean_script.replace("</script>", "")
        
        return jsonify({
            "status": "success",
            "script": clean_script,
            "entropy_div": entropy_div,
            "unique_div": unique_div
        })
    except Exception as e:
        print("[ERROR]", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


from db_utils import get_experiment_details_and_expressions  # or equivalent

@app.route('/get_experiment_metadata/<int:config_id>')
def get_experiment_metadata(config_id):
    try:
        details, expressions = get_experiment_details_and_expressions(config_id)
        return jsonify({
            "status": "success",
            "details": details,
            "expressions": expressions
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


from db_utils import get_entropy_and_histogram
from bokeh.plotting import figure
from bokeh.embed import components

def create_histogram_bokeh(histogram):
    expressions = [h["expression"] for h in histogram][:20]
    counts = [h["count"] for h in histogram][:20]

    p = figure(x_range=expressions, height=300, width=700,
               title="Top 20 Expressions", toolbar_location=None, tools="")
    p.vbar(x=expressions, top=counts, width=0.8)
    p.xaxis.major_label_orientation = 1.2
    p.xaxis.axis_label = "Expression"
    p.yaxis.axis_label = "Count"
    return components(p)

@app.route('/get_entropy_detail/<int:collision_number>')
def get_entropy_detail(collision_number):
    config_id = int(request.args.get("config_id"))
    result = get_entropy_and_histogram(config_id, collision_number)
    entropy = result["entropy"]
    histogram = result["histogram"]

    script, div = create_histogram_bokeh(histogram)

    return f"""
    <div class="card-header">
        <h3 class="card-title">Details for Collision {collision_number}</h3>
    </div>
    <div class="card-body">
        <p><strong>Entropy:</strong> {entropy:.4f}</p>
        <div>{div}</div>
    </div>
    <script>{script}</script>
    """


@app.route('/dashboard')
def dashboard():
    """Main dashboard with experiment list and overview statistics."""
    # Get latest 5 experiments
    experiments = get_experiment_configs()[:5]
    
    # Convert to more readable format
    experiment_list = [
        {
            'config_id': exp[0],
            'random_seed': exp[1],
            'generator_type': exp[2],
            'total_collisions': exp[3],
            'polling_frequency': exp[4],
            'timestamp': exp[5]
        } for exp in experiments
    ]
    
    # Count by generator type
    generator_counts = {}
    for exp in experiments:
        generator_type = exp[2]
        if generator_type in generator_counts:
            generator_counts[generator_type] += 1
        else:
            generator_counts[generator_type] = 1
    
    return render_template(
        'dashboard.html',
        experiments=experiment_list,
        generator_counts=generator_counts,
        total_experiments=len(experiments)
    )

if __name__ == '__main__':
    app.run(debug=True)