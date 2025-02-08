import os
import sys
import streamlit.web.bootstrap as bootstrap
from streamlit.web.server import Server

# Add your application directory to the Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

# Point to your virtual environment if you're using one
VENV_DIR = os.path.join(CURRENT_DIR, 'venv')
if os.path.exists(VENV_DIR):
    PYTHON_PATH = os.path.join(VENV_DIR, 'bin', 'python')
    if os.path.exists(PYTHON_PATH):
        os.environ['PYTHONPATH'] = PYTHON_PATH

		

def application(environ, start_response):
    # Set Streamlit page config
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    
    # Initialize Streamlit
    bootstrap.run('Home.py', '', [], flag_options={})
    
    # Get the Streamlit server instance
    server = Server.get_current()
    
    # Handle the WSGI request
    return server._wsgi_app(environ, start_response) 