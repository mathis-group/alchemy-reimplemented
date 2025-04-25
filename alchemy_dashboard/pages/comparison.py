import json
from bokeh.models import ColumnDataSource, Select, MultiSelect, Button, Div, HoverTool
from bokeh.layouts import column, row

from db_utils import (
    check_database_exists,
    get_experiments_from_db,
    get_experiment_details,
    process_collision_data
)
uploaded_files = []  
from styles import PLOT_COLORS
from plotting import create_styled_figure  


def create_comparison_view():
    """Create the multi-experiment comparison view"""
    comparison_div = Div(text="""
        <h2 class="section-title">Multi-Experiment Comparison</h2>
        <p style="margin-top: 0; color: #546E7A;">
            Compare metrics across multiple experiments to identify patterns and differences.
        </p>
    """, width=1200)

    source_select = Select(
        title="Data Source",
        options=[("database", "Database"), ("uploaded", "Uploaded Files")],
        value="database",
        width=370
    )

    experiment_select = MultiSelect(
        title="Select Experiments to Compare",
        options=[],
        value=[],
        height=150,
        width=370
    )

    metric_select = Select(
        title="Select Metric to Compare",
        options=[("entropy", "Entropy"), ("unique", "Unique Expressions"), ("total", "Total Expressions")],
        value="entropy",
        width=370
    )

    update_button = Button(
        label="Update Comparison",
        button_type="primary",
        width=370,
        css_classes=['menu-button']
    )

    comparison_plot = create_styled_figure("Experiment Comparison", "Collision Number", "Value", width=800, height=500)
    renderers = []

    def update_experiment_options(attr, old, new):
        if new == "database":
            if check_database_exists():
                experiments = get_experiments_from_db()
                options = [(str(exp[0]), f"Experiment {exp[0]}: {exp[1]} ({exp[4]})") for exp in experiments]
            else:
                options = []
        else:
            options = [(str(i), f['name']) for i, f in enumerate(uploaded_files)]
        experiment_select.options = options
        experiment_select.value = []

    def update_comparison():
        for renderer in renderers:
            comparison_plot.renderers.remove(renderer)
        renderers.clear()

        selected_metric = metric_select.value
        selected_experiments = experiment_select.value

        if not selected_experiments:
            return

        if selected_metric == "entropy":
            comparison_plot.yaxis.axis_label = "Entropy"
        elif selected_metric == "unique":
            comparison_plot.yaxis.axis_label = "Unique Expressions Count"
        else:
            comparison_plot.yaxis.axis_label = "Total Expressions"

        colors = PLOT_COLORS

        if source_select.value == "database":
            for i, exp_id in enumerate(selected_experiments):
                experiment, collisions, _ = get_experiment_details(int(exp_id))
                if not experiment:
                    continue
                df = process_collision_data(collisions)
                y_values = get_metric_series(df, selected_metric)
                color = colors[i % len(colors)]

                line = comparison_plot.line(
                    x=df['collision_number'],
                    y=y_values,
                    line_width=2.5,
                    color=color,
                    alpha=0.8,
                    legend_label=f"Experiment {exp_id}"
                )
                scatter = comparison_plot.scatter(
                    x=df['collision_number'],
                    y=y_values,
                    size=6,
                    color=color,
                    alpha=0.6
                )
                renderers.extend([line, scatter])
        else:
            for i, idx in enumerate(selected_experiments):
                idx = int(idx)
                if idx >= len(uploaded_files):
                    continue
                df = uploaded_files[idx]['data']
                name = uploaded_files[idx]['name']
                y_values = get_metric_series(df, selected_metric)
                color = colors[i % len(colors)]

                line = comparison_plot.line(
                    x=df['collision_number'],
                    y=y_values,
                    line_width=2.5,
                    color=color,
                    alpha=0.8,
                    legend_label=name
                )
                scatter = comparison_plot.scatter(
                    x=df['collision_number'],
                    y=y_values,
                    size=6,
                    color=color,
                    alpha=0.6
                )
                renderers.extend([line, scatter])

        comparison_plot.legend.click_policy = "hide"
        comparison_plot.legend.location = "top_right"

    def get_metric_series(df, metric):
        if metric == "entropy":
            return df['entropy']
        elif metric == "unique":
            return df['unique_expressions_count']
        return df['total_expressions']

    source_select.on_change('value', update_experiment_options)
    update_button.on_click(update_comparison)
    update_experiment_options(None, None, source_select.value)

    controls = column(
        Div(text="""
            <div class="card" style="padding: 15px 20px;">
                <h3 class="sub-title" style="margin-top: 0;">Comparison Controls</h3>
            </div>
        """, width=370),
        source_select,
        experiment_select,
        metric_select,
        update_button,
        width=400
    )

    return column(
        comparison_div,
        row(controls, column(
            Div(text='<div class="plot-container">', width=800),
            comparison_plot,
            Div(text='</div>', width=800)
        ))
    )
