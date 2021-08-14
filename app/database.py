from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask_googlemaps import GoogleMaps
from dash import Dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from flask_caching import Cache
from flask_compress import Compress
# from app.models import Report 
import jinja2


server = Flask(__name__)
Compress(server)

server.config['TESTING'] = True 
server.config['SECRET_KEY'] = 'TOTALLY NOT MY KEY' 
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reports.db'

config = {

    "DEBUG": True,         
    "CACHE_TYPE": "SimpleCache",  
    "CACHE_DEFAULT_TIMEOUT": 300
}

server.config.from_mapping(config)
db = SQLAlchemy(server)

