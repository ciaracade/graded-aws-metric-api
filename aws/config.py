"""
Generate fake AWS VPCs and subnets with different levels of usage
"""

import boto3
import random
import time
from typing import List, Dict

ec2 = boto3

class configAWS:
    