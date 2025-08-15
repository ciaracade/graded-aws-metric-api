"""
View generates a user interface for the user. Views are created by the data which
is collected by the model component but these data aren’t taken directly but through 
the controller. It only interacts with the controller.
"""

from flask import Flask
from controller.controller import controllerConfig

class viewConfig:
    def __init__(self, controller: controllerConfig):
        self.app = Flask(__name__)
        self.controller = controller

        @self.app.route("/")
        def index():
            return {"hello":"hello"}

    

        