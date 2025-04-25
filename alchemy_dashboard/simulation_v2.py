# import json
# import datetime
# import tempfile
# import traceback

# from bokeh.models import (
#     Div, Button, ColumnDataSource, NumericInput, RadioGroup,
#     Slider, TextInput, TextAreaInput, CheckboxGroup, HoverTool, CustomJS
# )
# from bokeh.layouts import column, row

# from styles import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR
# from plotting import create_styled_figure  


# def create_simulation_view():
#     """Create the simulation configuration and results view."""
#     header = Div(text="""
#         <h2 class="section-title">Run Simulation</h2>
#         <p style="margin-top: 0; color: #546E7A;">
#             Configure and run Alchemy experiments directly from the dashboard.
#         </p>
#     """, width=1200)

#     # === Inputs ===
#     total_collisions = NumericInput(value=1000, mode="int", title="Total Collisions", low=1, width=370)
#     polling_frequency = NumericInput(value=10, mode="int", title="Polling Frequency", low=1, width=370)
#     generator_select = RadioGroup(labels=["From File", "BTree", "Fontana"], active=0, width=370)
#     measurements = CheckboxGroup(labels=["Entropy", "Unique Expressions"], active=[0, 1], width=370)

#     # === Generator Parameters ===
#     file_input = TextInput(title="Expressions Filename", value="test_exprs.txt", width=370)
#     file_expressions = TextAreaInput(title="Or enter expressions directly (one per line):", value="", rows=5, width=370)

#     btree_size = NumericInput(value=5, mode="int", title="Size", low=1, width=370)
#     btree_fvp = Slider(start=0, end=1, value=0.5, step=0.1, title="Freevar Generation Probability", width=370)
#     btree_max_fv = NumericInput(value=3, mode="int", title="Max Free Variables", low=0, width=370)
#     btree_std = RadioGroup(labels=["Prefix", "Postfix", "None"], active=0, width=370)

#     fontana_abs_low = Slider(start=0, end=1, value=0.1, step=0.1, title="Abstraction Prob Range (Low)", width=370)
#     fontana_abs_high = Slider(start=0, end=1, value=0.5, step=0.1, title="Abstraction Prob Range (High)", width=370)
#     fontana_app_low = Slider(start=0, end=1, value=0.2, step=0.1, title="Application Prob Range (Low)", width=370)
#     fontana_app_high = Slider(start=0, end=1, value=0.6, step=0.1, title="Application Prob Range (High)", width=370)
#     fontana_max_depth = NumericInput(value=5, mode="int", title="Max Depth", low=1, width=370)
#     fontana_max_fv = NumericInput(value=2, mode="int", title="Max Free Variables", low=0, width=370)

#     # === Outputs ===
#     run_button = Button(label="Run Simulation", button_type="success", width=370, css_classes=['menu-button'])
#     status_div = Div(text="", width=800)
#     results_div = Div(text="", width=800)

#     entropy_source = ColumnDataSource(data=dict(x=[], y=[]))
#     unique_source = ColumnDataSource(data=dict(x=[], y=[]))
#     total_source = ColumnDataSource(data=dict(x=[], y=[]))

#     entropy_plot = create_styled_figure("Entropy Over Time", "Collision Number", "Entropy")
#     entropy_plot.line('x', 'y', source=entropy_source, line_width=2.5, color=PRIMARY_COLOR, line_alpha=0.8)
#     entropy_plot.add_tools(HoverTool(tooltips=[("Collision", "@x"), ("Entropy", "@y{0.0000}")], mode='vline'))

#     unique_plot = create_styled_figure("Unique Expressions Over Time", "Collision Number", "Count")
#     unique_plot.line('x', 'y', source=unique_source, line_width=2.5, color=SECONDARY_COLOR, line_alpha=0.8)
#     unique_plot.add_tools(HoverTool(tooltips=[("Collision", "@x"), ("Unique", "@y")], mode='vline'))

#     total_plot = create_styled_figure("Total Expressions Over Time", "Collision Number", "Count")
#     total_plot.line('x', 'y', source=total_source, line_width=2.5, color=ACCENT_COLOR, line_alpha=0.8)
#     total_plot.add_tools(HoverTool(tooltips=[("Collision", "@x"), ("Total", "@y")], mode='vline'))

#     def get_config():
#         config = {
#             "total_collisons": total_collisions.value,
#             "polling_frequency": polling_frequency.value,
#             "input_expressions": {
#                 "generator": "",
#                 "params": {}
#             },
#             "measurements": []
#         }

#         if generator_select.active == 0:
#             config["input_expressions"]["generator"] = "from_file"
#             config["input_expressions"]["params"] = {
#                 "filename": file_input.value,
#                 "direct_input": file_expressions.value.strip()
#             }
#         elif generator_select.active == 1:
#             config["input_expressions"]["generator"] = "BTree"
#             config["input_expressions"]["params"] = {
#                 "size": btree_size.value,
#                 "freevar_generation_probability": btree_fvp.value,
#                 "max_free_vars": btree_max_fv.value,
#                 "standardization": ["prefix", "postfix", "none"][btree_std.active]
#             }
#         elif generator_select.active == 2:
#             config["input_expressions"]["generator"] = "Fontana"
#             config["input_expressions"]["params"] = {
#                 "abs_range": [fontana_abs_low.value, fontana_abs_high.value],
#                 "app_range": [fontana_app_low.value, fontana_app_high.value],
#                 "max_depth": fontana_max_depth.value,
#                 "max_free_vars": fontana_max_fv.value
#             }

#         if 0 in measurements.active:
#             config["measurements"].append("entropy")
#         if 1 in measurements.active:
#             config["measurements"].append("unique_expressions")

#         return config

#     def on_run():
#         status_div.text = "Running simulation..."
#         results_div.text = ""

#         config = get_config()
#         success, result = run_simulation(config)

#         if success:
#             df = process_simulation_data(result)

#             entropy_source.data = {'x': df['collision_number'].tolist(), 'y': df['entropy'].tolist()}
#             unique_source.data = {'x': df['collision_number'].tolist(), 'y': df['unique_expressions_count'].tolist()}
#             total_source.data = {'x': df['collision_number'].tolist(), 'y': df['total_expressions'].tolist()}

#             results_div.text = f"""
#                 <div class="card">
#                     <h3 class="sub-title">Simulation Complete</h3>
#                     <div class="info-item"><span class="info-label">Generator:</span> {config["input_expressions"]["generator"]}</div>
#                     <div class="info-item"><span class="info-label">Total Collisions:</span> {config["total_collisons"]}</div>
#                 </div>
#             """

#             status_div.text = """
#                 <div style="background-color: #E8F5E9; color: #2E7D32; padding: 15px; border-radius: 5px;">
#                     <strong>Success!</strong> Simulation completed successfully.
#                 </div>
#             """
#         else:
#             status_div.text = """
#                 <div style="background-color: #FFEBEE; color: #C62828; padding: 15px; border-radius: 5px;">
#                     <strong>Error:</strong> Simulation failed.
#                 </div>
#             """
#             results_div.text = f"<pre>{result}</pre>"

#     run_button.on_click(on_run)

#     controls = column(
#         total_collisions,
#         polling_frequency,
#         generator_select,
#         file_input,
#         file_expressions,
#         btree_size,
#         btree_fvp,
#         btree_max_fv,
#         btree_std,
#         fontana_abs_low,
#         fontana_abs_high,
#         fontana_app_low,
#         fontana_app_high,
#         fontana_max_depth,
#         fontana_max_fv,
#         measurements,
#         run_button,
#         width=400
#     )

#     plots = column(
#         Div(text='<div class="plot-container">'),
#         entropy_plot,
#         unique_plot,
#         total_plot,
#         Div(text='</div>'),
#         results_div
#     )

#     return column(header, row(controls, column(status_div, plots)))


# from bokeh.embed import components
# from plotting import plot_simulation_metrics
# from utils import load_results

# def get_simulation_components():
#     """
#     Prepares Bokeh script and div components for embedding into HTML.
#     """
#     # Load your simulation results (adjust filename/path if needed)
#     results = load_results("results.json")

#     # Generate plots
#     entropy_fig = plot_entropy_over_time(results)
#     unique_expr_fig = plot_unique_expressions_over_time(results)

#     from bokeh.layouts import column
#     layout = column(entropy_fig, unique_expr_fig)
#     script, div = components(layout)
#     return script, div




# from bokeh.embed import components
# from plotting import plot_simulation_metrics
# from utils import load_results

# def get_simulation_components():
#     """
#     Prepares Bokeh script and div components for embedding into HTML.
#     """
#     # Load simulation result data (make sure results.json exists in the correct location)
#     results = load_results("results.json")

#     # Generate the two plots
#     entropy_fig, unique_expr_fig = plot_simulation_metrics(results)

#     from bokeh.layouts import column

#     layout = column(entropy_fig, unique_expr_fig)
#     script, div = components(layout)
#     return script, div




# import json

# def run_and_save_simulation():
#     """
#     Runs a basic simulation and saves the results to 'results.json'.
#     Replace this logic with your actual simulation engine.
#     """
#     # Dummy simulation example — replace with your real simulation logic
#     results = {
#         "time": list(range(10)),
#         "entropy": [0.1 * i for i in range(10)],
#         "unique_expressions": [10 + i * 2 for i in range(10)]
#     }

#     with open("results.json", "w") as f:
#         json.dump(results, f)

#     return results



# from bokeh.embed import components
# from plotting import plot_simulation_metrics
# from utils import load_results

# def get_simulation_components():
#     """
#     Runs the simulation, saves the results, and returns Bokeh script/div.
#     """
#     from simulation import run_and_save_simulation
#     results = run_and_save_simulation()

#     entropy_fig, unique_expr_fig = plot_simulation_metrics(results)

#     from bokeh.layouts import column

#     layout = column(entropy_fig, unique_expr_fig)
#     script, div = components(layout)
#     return script, div


import os
import json
import alchemy
import glob

def read_config_from_json(json_path: str) -> dict:
    with open(json_path, "r") as f:
        return json.load(f)

def run_experiment(config: dict, output_folder: str, run_id: int = 1) -> dict:
    os.makedirs(output_folder, exist_ok=True)

    generator_type = config["input_expressions"]["generator"]
    gen_params = config["input_expressions"].get("params", {})
    measurements = config.get("measurements", ["entropy", "unique_expressions", "len_unique_expressions"])

    soup = alchemy.PySoup()
    expressions = load_input_expressions(generator_type, gen_params)

    soup.perturb(expressions)
    total_collisions = config.get("total_collisions", 1000)
    polling_frequency = config.get("polling_frequency", 10)
    results_data = {}
    collision_count = 0

    while collision_count < total_collisions:
        soup.simulate_for(1, log=False)
        collision_count += 1
        if (collision_count % polling_frequency == 0) or (collision_count == total_collisions):
            key = f"collision_{collision_count}"
            step_data = {
                "state": soup.expressions()
            }
            if "entropy" in measurements:
                step_data["entropy"] = soup.population_entropy()
            if "unique_expressions" in measurements:
                step_data["unique_expressions"] = soup.unique_expressions()
            if "len_unique_expressions" in measurements:
                step_data["len_unique_expressions"] = len(soup.unique_expressions())
            results_data[key] = step_data

    last_key = sorted(results_data.keys(), key=lambda x: int(x.split("_")[-1]))[-1]
    last_state = {last_key: results_data[last_key]}

    output = {
        "config": config,
        "collisions_data": results_data,
        "last_state": last_state
    }

    output_path = os.path.join(output_folder, f"experiment_output_{run_id}.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=4)

    txt_path = os.path.join(output_folder, f"last_state_exprs_{run_id}.txt")
    with open(txt_path, "w") as f:
        for expr in last_state[last_key]["state"]:
            f.write(expr + "\n")

    return {"json_path": output_path, "txt_path": txt_path, "results": output}

def load_input_expressions(generator_type: str, gen_params: dict) -> list:
    if generator_type == "from_file":
        filename = gen_params.get("filename", "test_exprs.txt")
        if filename.endswith(".json"):
            with open(filename, "r") as f:
                data = json.load(f)
            collisions_data = data.get("collisions_data", {})
            all_keys = sorted(collisions_data.keys(), key=lambda x: int(x.split("_")[-1]))
            last_key = all_keys[-1]
            return collisions_data[last_key].get("state", [])
        else:
            with open(filename, "r") as f:
                return [line.strip() for line in f if line.strip()]
    elif generator_type == "BTree":
        return load_btree_expressions(gen_params)
    else:
        raise ValueError(f"Unsupported generator type: {generator_type}")

def load_btree_expressions(params: dict) -> list:
    size = params.get("size", 5)
    fvp = params.get("freevar_generation_probability", 0.5)
    max_fv = params.get("max_free_vars", 3)
    std_type = params.get("standardization", "prefix")
    num_expr = params.get("num_expressions", 10)

    btree_gen = alchemy.PyBTreeGen.from_config(
        size, fvp, max_fv, alchemy.PyStandardization(std_type)
    )
    return btree_gen.generate_n(num_expr)

def get_available_experiment_files(folder: str) -> list:
    files = glob.glob(os.path.join(folder, "experiment_output_*.json"))
    return sorted(files)

def get_last_txt_file(folder: str) -> str:
    txts = glob.glob(os.path.join(folder, "last_state_exprs_*.txt"))
    return sorted(txts)[-1] if txts else ""
