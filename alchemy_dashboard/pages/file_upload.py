# alchemy_dashboard/pages/file_upload.py

import json
from bokeh.models import (
    Div, ColumnDataSource, FileInput, Select, HoverTool
)
from bokeh.layouts import column, row

from utils import parse_uploaded_json, extract_data_from_json
from styles import (
    PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR
)
from plotting import create_styled_figure  

# Global uploaded file store
uploaded_files = []

def create_file_upload_view():
    """Create the file upload view for JSON experiment files."""
    upload_div = Div(text="""
        <h2 class="section-title">Upload Experiment Results</h2>
        <p style="margin-top: 0; color: #546E7A;">
            Upload JSON files containing experiment results to visualize them.
        </p>
    """, width=1200)

    file_input = FileInput(accept=".json", multiple=True)
    file_select = Select(title="Select Uploaded File", options=[], value=None, width=370)
    upload_status = Div(text="", width=400)
    metadata_div = Div(text="", width=400)

    # Data sources for visualizations
    entropy_source = ColumnDataSource(data=dict(x=[], y=[]))
    unique_source = ColumnDataSource(data=dict(x=[], y=[]))
    total_source = ColumnDataSource(data=dict(x=[], y=[]))

    # Plots
    entropy_plot = create_styled_figure("Entropy Over Time", "Collision Number", "Entropy")
    entropy_plot.line('x', 'y', source=entropy_source, color=PRIMARY_COLOR, line_width=2.5)
    entropy_plot.add_tools(HoverTool(tooltips=[("Collision", "@x"), ("Entropy", "@y{0.0000}")], mode='vline'))

    unique_plot = create_styled_figure("Unique Expressions Over Time", "Collision Number", "Count")
    unique_plot.line('x', 'y', source=unique_source, color=SECONDARY_COLOR, line_width=2.5)
    unique_plot.add_tools(HoverTool(tooltips=[("Collision", "@x"), ("Unique", "@y")], mode='vline'))

    total_plot = create_styled_figure("Total Expressions Over Time", "Collision Number", "Count")
    total_plot.line('x', 'y', source=total_source, color=ACCENT_COLOR, line_width=2.5)
    total_plot.add_tools(HoverTool(tooltips=[("Collision", "@x"), ("Total", "@y")], mode='vline'))

    # File upload handler
    def handle_file_upload(attr, old, new):
        if not new:
            return

        json_data = parse_uploaded_json(new)
        if json_data:
            result = extract_data_from_json(json_data)
            if result:
                index = len(uploaded_files)
                name = f"File {index+1}: {result['metadata'].get('generator_type', 'Unknown')}"
                uploaded_files.append({
                    'name': name,
                    'metadata': result['metadata'],
                    'data': result['processed_data']
                })
                file_select.options = [(str(i), f['name']) for i, f in enumerate(uploaded_files)]
                file_select.value = str(index)

                upload_status.text = f"""
                <div style="background-color: #E8F5E9; color: #2E7D32; padding: 10px; border-radius: 5px;">
                    <strong>Success:</strong> Uploaded and parsed {name}
                </div>
                """
            else:
                upload_status.text = error_box("Could not extract data from the file.")
        else:
            upload_status.text = error_box("Invalid JSON file.")

    # File select handler
    def update_plots(attr, old, new):
        if new is None:
            return
        index = int(new)
        if index >= len(uploaded_files):
            return

        selected = uploaded_files[index]
        metadata = selected['metadata']
        df = selected['data']

        # Update metadata
        metadata_div.text = f"""
        <div class="info-panel">
            <h3 class="sub-title">Experiment Metadata</h3>
            <div class="info-item"><span class="info-label">Generator:</span> {metadata.get('generator_type')}</div>
            <div class="info-item"><span class="info-label">Total Collisions:</span> {metadata.get('total_collisions')}</div>
            <div class="info-item"><span class="info-label">Polling Frequency:</span> {metadata.get('polling_frequency')}</div>
            <div class="info-item"><span class="info-label">Generator Params:</span>
                <div class="code-block">{json.dumps(metadata.get('generator_params', {}), indent=2)}</div></div>
            <div class="info-item"><span class="info-label">Measurements:</span>
                <div class="code-block">{json.dumps(metadata.get('measurements', []), indent=2)}</div></div>
        </div>
        """

        entropy_source.data = {
            'x': df['collision_number'].tolist(),
            'y': df['entropy'].tolist()
        }
        unique_source.data = {
            'x': df['collision_number'].tolist(),
            'y': df['unique_expressions_count'].tolist()
        }
        total_source.data = {
            'x': df['collision_number'].tolist(),
            'y': df['total_expressions'].tolist()
        }

    # Reusable error message box
    def error_box(msg):
        return f"""
        <div style="background-color: #FFEBEE; color: #C62828; padding: 10px; border-radius: 5px;">
            <strong>Error:</strong> {msg}
        </div>
        """

    # Connect callbacks
    file_input.on_change('value', handle_file_upload)
    file_select.on_change('value', update_plots)

    upload_instructions = Div(text="""
        <div class="card">
            <h3 class="sub-title">Upload Instructions</h3>
            <p>1. Upload one or more experiment JSON files</p>
            <p>2. Use the dropdown to select a file to visualize</p>
        </div>
    """, width=400)

    plot_section = column(
        Div(text='<div class="plot-container">'),
        entropy_plot, unique_plot, total_plot,
        Div(text='</div>')
    )

    return column(
        upload_div,
        row(
            column(upload_instructions, file_input, upload_status, file_select, metadata_div, width=400),
            plot_section
        )
    )
