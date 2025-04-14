# alchemy_dashboard/pages/welcome.py

from bokeh.models import Div
from styles import CUSTOM_CSS


def create_welcome_view():
    """Create the welcome view shown on application launch."""
    return Div(text=f"""
        {CUSTOM_CSS}
        <div class="welcome-card">
            <h2 style="color: #3949AB; margin-top: 0;">Welcome to the Alchemy Experiment Visualizer</h2>
            <p>Select an option from the menu above to get started.</p>

            <div class="welcome-features">
                <div class="feature-item">
                    <h4>Database Visualization</h4>
                    <p>View experiments from your local database with interactive charts</p>
                </div>
                <div class="feature-item">
                    <h4>Upload Results JSON</h4>
                    <p>Upload and visualize experiment results from JSON files</p>
                </div>
                <div class="feature-item">
                    <h4>Multi-Experiment Comparison</h4>
                    <p>Compare multiple experiments side-by-side</p>
                </div>
                <div class="feature-item">
                    <h4>Time Series Analysis</h4>
                    <p>Analyze experiment data over time (coming soon)</p>
                </div>
            </div>
        </div>
    """, width=1200)
