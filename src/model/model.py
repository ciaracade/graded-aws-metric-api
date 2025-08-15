"""
Model corresponds to all the data-related logic that the user works with
transferred between the View and Controller components or etc.
"""
from controller.controller import controllerConfig
from aws.config import AWSConfig

class modelConfig:
    def __init__(self, client):
        self.client = client

    

