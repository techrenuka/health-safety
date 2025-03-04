import os
import sys

# Add your application directory to the Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

# Point to your virtual environment if you're using one
VENV_DIR = os.path.join(CURRENT_DIR, 'venv')
if os.path.exists(VENV_DIR):
    PYTHON_PATH = os.path.join(VENV_DIR, 'bin', 'python')
    if os.path.exists(PYTHON_PATH):
        os.environ['PYTHONPATH'] = PYTHON_PATH

# Import your Streamlit application
from Home import app

# WSGI application callable
application = app 