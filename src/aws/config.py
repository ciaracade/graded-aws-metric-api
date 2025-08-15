"""
Generates AWS VPCs and subnets with different levels of utilization
via LocalStack
"""

import boto3
from botocore.config import Config
import random
import time
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class AWSConfig:
    """AWS configuration for LocalStack development environment"""

    # Configuration for LocalStack boto3 config 
    _config = Config(
        region_name='us-east-1',
        signature_version='v4',
        retries={
            'max_attempts': 10,
            'mode': 'standard'
        }
    )
    
    _endpoint_url = 'http://localhost:4566'
    _aws_access_key_id = 'test'
    _aws_secret_access_key = 'test'

    def __init__(self):
        """Initialize AWS configuration"""
        self.ec2 = self.get_ec2_client()

    @classmethod
    def get_ec2_client(cls):
        """Get configured EC2 client for LocalStack"""


        return boto3.client(
            'ec2',
            config=cls._config,
            endpoint_url=cls._endpoint_url,
            aws_access_key_id=cls._aws_access_key_id,
            aws_secret_access_key=cls._aws_secret_access_key
        )
    
