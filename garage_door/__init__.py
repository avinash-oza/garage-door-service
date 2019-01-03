from flask import Flask
from flask_restplus import Api

app = Flask(__name__)

app.config.from_mapping({'GENERAL_HOSTNAME': 'DEFAULT_HOST'})
if not app.config.from_envvar('APP_SETTINGS', silent=True):
    print("Did not find a config to load")

api = Api(app)
import garage_door.garage_door_server
