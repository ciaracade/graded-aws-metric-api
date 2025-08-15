"""
Controller is the component that enables the interconnection between the views and
the model so it acts as an intermediary
"""

from model.model import modelConfig


class controllerConfig:
    def __init__(self, model: modelConfig):
        self.model = model
