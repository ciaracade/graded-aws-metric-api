from flask import Flask
from controller.controller import controller
from aws.config import AWSConfig
from view.view import view

def create_api():
    client = AWSConfig()
    controller = controller
    view = view(controller)

    return view.app


if __name__ == "__main__":
    app = create_api() # Initialize flask app through views
    app.run(debug=True)