# alchemy_dashboard/styles.py

# === Color Palette ===
PRIMARY_COLOR = "#3949AB"       # Indigo
SECONDARY_COLOR = "#00ACC1"     # Cyan
ACCENT_COLOR = "#FF6E40"        # Deep Orange
BACKGROUND_COLOR = "#FAFAFA"    # Off-white
TEXT_COLOR = "#263238"          # Blue Grey
GRID_COLOR = "#E0E0E0"          # Light Grey

PLOT_COLORS = [
    PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR,
    "#7CB342", "#8E24AA", "#FFA000", "#D81B60", "#00897B"
]

# === Custom CSS for Dashboard Styling ===
CUSTOM_CSS = """
<style>
    html, body {
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
        overflow-x: hidden;
        font-family: 'Roboto', 'Helvetica Neue', Helvetica, Arial, sans-serif;
        background-color: #FAFAFA;
        color: #263238;
    }

    .dashboard-header {
        background: linear-gradient(90deg, #3949AB, #00ACC1);
        padding: 20px 30px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        color: white;
    }

    .section-title {
        font-size: 24px;
        font-weight: 500;
        margin-bottom: 12px;
        color: #3949AB;
        border-bottom: 2px solid #E0E0E0;
        padding-bottom: 10px;
    }

    .sub-title {
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 8px;
        color: #00ACC1;
    }

    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    .menu-button {
        transition: all 0.2s ease;
        border-radius: 8px;
    }

    .menu-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }

    .nav-menu {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        justify-content: center;
        margin-bottom: 30px;
    }

    .welcome-card {
        text-align: center;
        padding: 40px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 3px 15px rgba(0, 0, 0, 0.05);
    }

    .welcome-features {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 15px;
        margin-top: 25px;
    }

    .feature-item {
        background: #F5F5F5;
        padding: 15px 20px;
        border-radius: 8px;
        border-left: 4px solid #3949AB;
        text-align: left;
        width: 220px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }

    .feature-item h4 {
        margin: 0 0 10px 0;
        color: #3949AB;
    }

    .feature-item p {
        margin: 0;
        font-size: 14px;
        color: #455A64;
    }

    .plot-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    .info-panel {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    .info-item {
        margin-bottom: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid #E0E0E0;
    }

    .info-item:last-child {
        border-bottom: none;
    }

    .info-label {
        font-weight: 500;
        color: #455A64;
    }

    .code-block {
        background: #F5F5F5;
        padding: 12px;
        border-radius: 6px;
        font-family: monospace;
        white-space: pre-wrap;
        overflow-x: auto;
    }

    button.bk-btn {
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    .bk-btn {
        font-size: 28px !important;
        font-weight: 500 !important;
        padding: 15px 20px !important;
        line-height: 1.2 !important;
        height: auto !important;
    }

    button.bk-btn-primary {
        background-color: #3949AB !important;
    }

    button.bk-btn-primary:hover {
        background-color: #303F9F !important;
    }

    .bk-btn-success {
        background-color: #43A047 !important;
    }

    .bk-btn-success:hover {
        background-color: #388E3C !important;
    }

    select, .bk-input {
        border-radius: 6px !important;
        border: 1px solid #CFD8DC !important;
        padding: 8px 12px !important;
        transition: all 0.2s ease;
    }

    select:focus, .bk-input:focus {
        border-color: #3949AB !important;
        box-shadow: 0 0 0 2px rgba(57, 73, 171, 0.25) !important;
    }
</style>
"""
