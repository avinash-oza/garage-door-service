
from flask import Flask
from flask_restplus import Api

#TODO: REMOVE THIS CODE


app = Flask(__name__)

app.config.from_envvar('APP_SETTINGS')
api = Api(app)