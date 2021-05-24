from flask import Flask
import dash
import dash_bootstrap_components as dbc

# spin up Flask server - running Flask server because running Dash through Flask
server = Flask(__name__)

server.config['DEBUG'] = True

# The url_base_pathname is what goes after the last / in the url address
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP], #Used for styling dashboard.py
    server=server,
    title='Empl Attrition Analysis', # This is the tab title
    url_base_pathname='/dashboard/')

server = app.server

# Helps with debugging - if dashboard doesn't spin up correctly, this should show traceback errors
app.config['suppress_callback_exceptions']=True

# Import the routes.py file
# Need to specify emp_attrition because run.py is outside/next to the project folder
from emp_attrition import routes