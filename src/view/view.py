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
        def healthcheck():
            return {
                "status": "healthy",
                "service": "AWS VPC Health and Utilization Metric API",
                "version": "1.0.0",
            }
        
        @self.app.route("/vpc")
        def get_all_vpcs():
            try:
                vpcs = self.controller.get_all_vpcs()
                return {"vpcs": vpcs, "count": len(vpcs)}, 200
            except Exception as e:
                return {"error": str(e)}, 500
        
        @self.app.route("/vpc/<vpc_id>")
        def get_vpc_by_id(vpc_id):
            try:
                vpc = self.controller.get_vpc_details(vpc_id)
                if vpc:
                    return {"vpc": vpc}, 200
                else:
                    return {"error": f"VPC {vpc_id} not found"}, 404
            except Exception as e:
                return {"error": str(e)}, 500
        
        @self.app.route("/vpc/<vpc_id>/grade")
        def grade_vpc(vpc_id):
            try:
                grade = self.controller.grade_vpc(vpc_id)
                if grade:
                    return {"grade": grade}, 200
                else:
                    return {"error": f"VPC {vpc_id} not found"}, 404
            except Exception as e:
                return {"error": str(e)}, 500
