from flask import Flask
from flask_restplus import Api

app = Flask(__name__)

from .status import api as ns1

api = Api(app)
api.add_namespace(ns1)
import garage_door.endpoints
