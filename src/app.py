from controller.controller import controllerConfig
from model.model import modelConfig
from aws.config import AWSConfig
from view.view import viewConfig
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Initializes app through views
def create_api():
    aws_config = AWSConfig()
    client = aws_config.ec2
    model = modelConfig(client)
    controller = controllerConfig(model)
    view = viewConfig(controller)
    return view.app


if __name__ == "__main__":
    app = create_api() 
    app.run(debug=True)
