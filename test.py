# from alchemy import (
#     PySoup, PyReactor, PyStandardization, PyBTreeGen
# )
# from bokeh.plotting import figure, show
# from bokeh.models import ColumnDataSource
# from bokeh.layouts import column
# import random

# def generate_and_plot():
#     # Initialize PyReactor and PySoup
#     reactor = PyReactor()
#     soup = PySoup()

#     # Create a PyStandardization object
#     std = PyStandardization("prefix")

#     # Generate terms using PyBTreeGen
#     btree_gen = PyBTreeGen.from_config(
#         size=20,  # Number of terms in the BTree
#         freevar_generation_probability=0.3,
#         max_free_vars=5,
#         std=std
#     )
    
#     generated_terms = btree_gen.generate_n(100)  # Generate 100 terms
    
#     # Perturb the soup with generated terms
#     soup.perturb(generated_terms)

#     # Get unique expressions and their counts
#     unique_expressions = soup.unique_expressions()
#     expression_counts = soup.expression_counts()

#     # Prepare data for visualization
#     expressions, counts = zip(*expression_counts)
#     data_source = ColumnDataSource(data={"expressions": expressions, "counts": counts})

#     # Create a Bokeh figure
#     plot = figure(
#         title="Expression Frequency Distribution",
#         width=1000,
#         height=600,
#         x_axis_label="Expressions",
#         y_axis_label="Counts",
#         x_range=list(expressions),  # Convert expressions to a list
#     )
    
#     plot.vbar(x="expressions", top="counts", width=0.8, source=data_source)
#     plot.xaxis.major_label_orientation = "vertical"

#     # Simulate entropy series data for another visualization
#     entropy_values = [random.random() for _ in range(len(unique_expressions))]
#     steps = list(range(len(entropy_values)))  # Convert range to a list
#     entropy_plot = figure(
#         title="Simulated Entropy Values",
#         width=1000,
#         height=400,
#         x_axis_label="Step",
#         y_axis_label="Entropy"
#     )
#     entropy_plot.line(steps, entropy_values, line_width=2)

#     # Display both plots
#     show(column(plot, entropy_plot))

# if __name__ == "__main__":
#     generate_and_plot()
import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import column

# --- Sample Data: Replace with your actual data ---
expressions = ["exp1", "exp2", "exp3", "exp4", "exp5"]
frequencies = [10, 15, 5, 20, 25]
steps = np.arange(1, 101)
entropy_values = np.random.rand(100)

# Set output file to save the results
output_file("alchemy_plots.html", title="Alchemy Plots")

# --- Generate Cumulative Distribution Plot ---
# Sort expressions and frequencies
sorted_indices = np.argsort(frequencies)
sorted_expressions = [expressions[i] for i in sorted_indices]
sorted_frequencies = np.array([frequencies[i] for i in sorted_indices])

# Calculate cumulative frequencies and normalize
cumulative_frequencies = np.cumsum(sorted_frequencies)
normalized_cumulative = cumulative_frequencies / cumulative_frequencies[-1]

# Create the cumulative distribution plot
cumulative_plot = figure(
    title="Cumulative Distribution of Expression Frequencies",
    x_axis_label="Expressions",
    y_axis_label="Cumulative Frequency (Normalized)",
    x_range=sorted_expressions,
    tools="pan,wheel_zoom,box_zoom,reset",
    width=800,
    height=400,
)

cumulative_plot.line(
    x=sorted_expressions,
    y=normalized_cumulative,
    line_width=2,
    color="blue",
    legend_label="Cumulative Distribution",
)

cumulative_plot.circle(
    x=sorted_expressions,
    y=normalized_cumulative,
    size=8,
    color="red",
    legend_label="Data Points",
)

cumulative_plot.legend.location = "top_left"

# --- Generate Entropy vs Step Plot ---
entropy_plot = figure(
    title="Simulated Entropy Values",
    x_axis_label="Step",
    y_axis_label="Entropy",
    width=800,
    height=400,
)

entropy_plot.line(
    x=steps,
    y=entropy_values,
    line_width=2,
    color="green",
    legend_label="Entropy",
)

# --- Display Plots Together ---
show(column(cumulative_plot, entropy_plot))

