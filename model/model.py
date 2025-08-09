"""
Model corresponds to all the data-related logic that the user works with
transferred between the View and Controller components or etc.
"""
from controller.controller import controller
class model:
    def __init__(self, controller):
        self.controller = controller

    

