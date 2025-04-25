import sqlite3
import pandas as pd
from bokeh.models import ColumnDataSource, Legend, LegendItem, HoverTool, Div
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column

# will need to change based on locaiton
db_name = '/Users/jjoseph/Desktop/Projects/AICHEMY_VISUALISER/database/alchemy_data.db'

def fetch_experiment_tables():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'experiment_%'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def fetch_experiment_data(table_name):
    conn = sqlite3.connect(db_name)
    query = f"SELECT series_number, lambda_expression FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['time_step'] = range(len(df))
    df['unique_entropy'] = df['lambda_expression'].apply(len)
    df['unique_expressions'] = df['lambda_expression'].apply(lambda x: len(set(x)))
    return df

experiment_tables = {}
for table_name in fetch_experiment_tables():
    experiment_tables[table_name] = fetch_experiment_data(table_name)

line_renderers = []
line_to_table_map = {}
data_map = {}
source2 = ColumnDataSource(data=dict(time_step=[], unique_expressions=[]))

intro_text = Div(text="""
    <h1>Bokeh Data Visualization</h1>
""", width=1200)

#Plots
p1 = figure(
    title="Unique Entropy Over Time (All Experiments)",
    x_axis_label="Time",
    y_axis_label="Unique Entropy",
    width=1800,
    height=900,
    tools="tap,pan,box_zoom,wheel_zoom,reset"
)

p2 = figure(
    title="Number of Unique Expressions Over Time (Selected Experiment)",
    x_axis_label="Time",
    y_axis_label="Number of Unique Expressions",
    width=1800,
    height=900,
    tools="pan,box_zoom,wheel_zoom,reset"
)

p2.line('time_step', 'unique_expressions', source=source2, line_width=2, color="green")

legend_items1 = []
colors = ['blue', 'green', 'red']
for idx, (table_name, full_df) in enumerate(experiment_tables.items()):
    source1 = ColumnDataSource(data=dict(
        time_step=full_df['time_step'],
        unique_entropy=full_df['unique_entropy']
    ))

    data_map[table_name] = {'time_step': full_df['time_step'], 'unique_expressions': full_df['unique_expressions']}

    color = colors[idx % len(colors)]
    line1 = p1.line('time_step', 'unique_entropy', source=source1, line_width=2, color=color, name=table_name)
    line_renderers.append(line1)
    line_to_table_map[line1] = table_name
    legend_items1.append(LegendItem(label=table_name, renderers=[line1]))

hover = HoverTool(
    tooltips=[
        ("Experiment", "$name"),
        ("Time Step", "@time_step"),
        ("Unique Entropy", "@unique_entropy"),
    ],
    mode='mouse'  # Hover only when directly over the line
)
p1.add_tools(hover)

legend1 = Legend(items=legend_items1)
p1.add_layout(legend1, 'right')
p1.legend.click_policy = "hide"

def update_second_plot(event):
    closest_renderer = None
    min_distance = float('inf')

    for renderer in line_renderers:
        if renderer.visible:
            distances = ((renderer.data_source.data['time_step'] - event.x) ** 2).min()
            if distances < min_distance:
                min_distance = distances
                closest_renderer = renderer

    if closest_renderer and closest_renderer in line_to_table_map:
        selected_table = line_to_table_map[closest_renderer]
        print(f"Selected experiment: {selected_table}")
        source2.data = dict(
            time_step=data_map[selected_table]['time_step'],
            unique_expressions=data_map[selected_table]['unique_expressions']
        )

p1.on_event('tap', update_second_plot)

layout = column(intro_text, p1, p2, sizing_mode="stretch_both")
curdoc().add_root(layout)
curdoc().title = "Bokeh App"
