from bokeh.models import Div
from bokeh.layouts import column


def create_time_series_view():
    """Create the time series analysis view (placeholder)."""
    time_series_div = Div(text="""
        <h2 class="section-title">Time Series Analysis</h2>
        <p style="margin-top: 0; color: #546E7A;">
            Analyze experiment data over time with advanced visualizations.
            This feature is under development.
        </p>
    """, width=1200)

    return column(time_series_div)
