from bokeh.models import Div, Select, ColumnDataSource, HoverTool
from bokeh.layouts import column, row
from db_utils import (
    check_database_exists,
    get_experiments_from_db,
    get_experiment_details,
    process_collision_data
)
from styles import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR
from plotting import create_styled_figure



def create_db_visualization_view():
    """Create the database visualization view"""
    if not check_database_exists():
        return column(
            Div(text="""
                <div class="card">
                    <h2 class="section-title">Database Visualization</h2>
                    <p>No database found. Please run some experiments first or upload JSON files.</p>
                </div>
            """, width=1200)
        )

    experiments = get_experiments_from_db()
    if not experiments:
        return column(
            Div(text="""
                <div class="card">
                    <h2 class="section-title">Database Visualization</h2>
                    <p>No experiments found in the database.</p>
                </div>
            """, width=1200)
        )

    experiment_options = [(str(exp[0]), f"Experiment {exp[0]}: {exp[1]} ({exp[4]})") for exp in experiments]
    experiment_select = Select(title="Select Experiment", options=experiment_options, value=experiment_options[0][0])

    entropy_source = ColumnDataSource(data=dict(x=[], y=[]))
    unique_source = ColumnDataSource(data=dict(x=[], y=[]))
    total_source = ColumnDataSource(data=dict(x=[], y=[]))

    entropy_plot = create_styled_figure("Entropy Over Time", "Collision Number", "Entropy")
    entropy_plot.line('x', 'y', source=entropy_source, line_width=2.5, color=PRIMARY_COLOR, line_alpha=0.8)
    entropy_plot.scatter('x', 'y', source=entropy_source, size=6, color=PRIMARY_COLOR, alpha=0.6)
    entropy_plot.add_tools(HoverTool(tooltips=[("Collision", "@x"), ("Entropy", "@y{0.0000}")], mode='vline'))

    unique_plot = create_styled_figure("Unique Expressions Over Time", "Collision Number", "Count")
    unique_plot.line('x', 'y', source=unique_source, line_width=2.5, color=SECONDARY_COLOR, line_alpha=0.8)
    unique_plot.scatter('x', 'y', source=unique_source, size=6, color=SECONDARY_COLOR, alpha=0.6)
    unique_plot.add_tools(HoverTool(tooltips=[("Collision", "@x"), ("Unique Expressions", "@y")], mode='vline'))

    total_plot = create_styled_figure("Total Expressions Over Time", "Collision Number", "Count")
    total_plot.line('x', 'y', source=total_source, line_width=2.5, color=ACCENT_COLOR, line_alpha=0.8)
    total_plot.scatter('x', 'y', source=total_source, size=6, color=ACCENT_COLOR, alpha=0.6)
    total_plot.add_tools(HoverTool(tooltips=[("Collision", "@x"), ("Total Expressions", "@y")], mode='vline'))

    details_div = Div(text="<h3 class='sub-title'>Experiment Details</h3>", width=800)
    expressions_div = Div(text="<h3 class='sub-title'>Initial Expressions</h3>", width=800)

    def update_plots(experiment_id):
        experiment, collisions, expressions = get_experiment_details(int(experiment_id))
        if experiment:
            exp_id, total_collisions, polling_frequency, generator_type, generator_params_json, measurements_json, timestamp = experiment
            try:
                import json
                generator_params = json.loads(generator_params_json) if generator_params_json else {}
                measurements = json.loads(measurements_json) if measurements_json else []
            except:
                generator_params = {}
                measurements = []

            details_html = f"""
            <div class="info-panel">
                <h3 class="sub-title">Experiment {exp_id} Details</h3>
                <div class="info-item"><span class="info-label">Generator:</span> {generator_type}</div>
                <div class="info-item"><span class="info-label">Total Collisions:</span> {total_collisions}</div>
                <div class="info-item"><span class="info-label">Polling Frequency:</span> {polling_frequency}</div>
                <div class="info-item"><span class="info-label">Timestamp:</span> {timestamp}</div>
                <div class="info-item"><span class="info-label">Generator Parameters:</span><div class="code-block">{json.dumps(generator_params, indent=2)}</div></div>
                <div class="info-item"><span class="info-label">Measurements:</span><div class="code-block">{json.dumps(measurements, indent=2)}</div></div>
            </div>
            """
            details_div.text = details_html

            expr_html = """
            <div class="info-panel">
                <h3 class="sub-title">Initial Expressions</h3>
                <ul style="padding-left: 20px; margin-top: 10px;">
            """
            for expr in expressions:
                expr_html += f'<li style="margin-bottom: 8px; font-family: monospace;">{expr[0]}</li>'
            expr_html += "</ul></div>"
            expressions_div.text = expr_html

            df = process_collision_data(collisions)
            entropy_source.data = { 'x': df['collision_number'].tolist(), 'y': df['entropy'].tolist() }
            unique_source.data = { 'x': df['collision_number'].tolist(), 'y': df['unique_expressions_count'].tolist() }
            total_source.data = { 'x': df['collision_number'].tolist(), 'y': df['total_expressions'].tolist() }
        else:
            details_div.text = '<div class="info-panel"><h3 class="sub-title">Experiment not found</h3></div>'
            expressions_div.text = ""

    update_plots(experiment_options[0][0])
    experiment_select.on_change('value', lambda attr, old, new: update_plots(new))

    selector_div = Div(text="""
        <div class="card" style="padding: 15px 20px;">
            <h3 class="sub-title" style="margin-top: 0;">Experiment Selection</h3>
        </div>
    """, width=300)

    plots_div = Div(text='<h3 class="sub-title">Experiment Metrics</h3>', width=800)
    plots = column(plots_div, entropy_plot, unique_plot, total_plot)

    return column(
        Div(text='<h2 class="section-title">Database Visualization</h2>', width=1200),
        row(column(selector_div, experiment_select, width=300), column(plots)),
        details_div,
        expressions_div
    )
