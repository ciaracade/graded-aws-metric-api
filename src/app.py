from flask import Flask
from controller.controller import controllerConfig
from model.model import modelConfig
from aws.config import AWSConfig
from view.view import viewConfig
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_api():
    client = AWSConfig.get_ec2_client()
    model = modelConfig(client)
    controller = controllerConfig(model)
    view = viewConfig(controller)
    return view.app

if __name__ == "__main__":
    app = create_api() # Initialize flask app through views
    app.run(debug=True)