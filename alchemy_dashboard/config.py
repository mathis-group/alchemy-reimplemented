# alchemy_dashboard/config.py

# === Application Configuration ===

# SQLite database filename
DB_NAME = 'alchemy_experiments.db'

# Path settings (if needed later)
DATA_DIR = 'data/'
STATIC_DIR = 'static/'

# Feature toggles
ENABLE_EXPERIMENT_DOWNLOAD = True
ENABLE_TIME_SERIES_VIEW = True  # can turn off for MVP

# App metadata
APP_TITLE = "Alchemy Experiment Dashboard"
