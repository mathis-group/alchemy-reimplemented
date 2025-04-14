import json
from bokeh.embed import components
from bokeh.layouts import column
from plotting import plot_simulation_metrics

def get_simulation_components(results_path: str):
    """
    Load results from JSON, generate Bokeh layout, return script and div.
    """
    with open(results_path, "r") as f:
        results = json.load(f)

    layout = plot_simulation_metrics(results)
    script, div = components(column(layout))
    return script, div
