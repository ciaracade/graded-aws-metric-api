"""
Generates AWS VPCs and subnets with different levels of utilization
via LocalStack
"""

import boto3
from botocore.config import Config
from dotenv import load_dotenv
import logging
import os, random, math

logger = logging.getLogger(__name__)
load_dotenv()

# Initialize random values for VPC/Subnet creation
VPC_MIN  = int(os.getenv("VPC_MIN", "1"))
VPC_MAX  = int(os.getenv("VPC_MAX", "3"))
SUBNET_MIN = int(os.getenv("SUBNET_MIN", "2"))
SUBNET_MAX = int(os.getenv("SUBNET_MAX", "5"))
UTIL_LOW   = float(os.getenv("UTIL_LOW", "0.05"))
UTIL_HIGH  = float(os.getenv("UTIL_HIGH", "0.95"))
SEED = os.getenv("RAND_SEED")
if SEED is not None:
    random.seed(int(SEED))





class AWSConfig:
    """AWS configuration for LocalStack development environment"""

    # Configuration for LocalStack boto3 config
    _config = Config(
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        signature_version="v4",
        retries={"max_attempts": 10, "mode": "standard"},
    )

    _endpoint_url = os.getenv("ENDPOINT_URL", "http://localhost:4566")
    _aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "test")
    _aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "test")

    def __init__(self):
        """Initialize AWS configuration"""
        self.ec2 = self.get_ec2_client()
        self.seed_cloud(self.ec2)


    @classmethod
    def get_ec2_client(cls):
        """Get configured EC2 client for LocalStack"""
        logger.info("AWS EC2 Client initializing...")
        try:
            logger.info("AWS EC2 Client initialized")
            return boto3.client(
                "ec2",
                config=cls._config,
                endpoint_url=cls._endpoint_url,
                aws_access_key_id=cls._aws_access_key_id,
                aws_secret_access_key=cls._aws_secret_access_key,
            )
        except Exception as e:
            logger.error(f"Failed to create EC2 client: {e}")
            raise
    
    def seed_cloud(self, ec2: boto3.client):
        """ Seeds AWS EC2 instance with VPCs of various subnet utilizations """
        self.check_ranges()

        # Create randoms for VPC and subnet rangs
        vpc_count = random.randint(VPC_MIN, VPC_MAX)

        # Create vpc
        for vpc_idx in range(1, vpc_count+1):
            logger.info(f"Creating VPC #{vpc_idx}...")
            try:
                subnet_count = random.randint(SUBNET_MIN, SUBNET_MAX)
                for subnet_idx in range(1, subnet_count+1):
                    logger.info(f"Creating subnet #{subnet_idx}...")
                    try:
                        logger.info(f"Created subnet #{subnet_idx}")
                    except Exception as e:
                        logger.error(f"Failed to create subnet #{subnet_idx} in VPC #{vpc_idx}: {e}")
                        raise
                logger.info(f"Created VPC #{vpc_idx}")
            except Exception as e:
                logger.error(f"Failed to create VPC #{vpc_idx}: {e}")
                raise


        # Creates subnet in vpc 
     
    def create_vpc(self):
        """ Creates VPC """
        
    def create_subnet(self):
        """ Creates subnet """

    def get_vpc(self):
        """ Gets VPC """
        
    def get_subnet(self):
        """ Gets subnet """
    
    def check_ranges(self):
        """ 
        Checks ranges on VPC/Subnet creation limits and utilization ranges to make
        sure high >= low and minimums are not zero.
        """
        if VPC_MIN <= 0:
            raise ValueError(f"VPC_MIN ({VPC_MIN}) must be > 0")
        
        if SUBNET_MIN <= 0:
            raise ValueError(f"SUBNET_MIN ({SUBNET_MIN}) must be > 0")
        
        if VPC_MAX < VPC_MIN:
            raise ValueError(f"VPC_MAX ({VPC_MAX}) must be >= VPC_MIN ({VPC_MIN})")
        
        if SUBNET_MAX < SUBNET_MIN:
            raise ValueError(f"SUBNET_MAX ({SUBNET_MAX}) must be >= SUBNET_MIN ({SUBNET_MIN})")
        
        if UTIL_HIGH < UTIL_LOW:
            raise ValueError(f"UTIL_HIGH ({UTIL_HIGH}) must be >= UTIL_LOW ({UTIL_LOW})")
        
        logger.info("All ranges validated successfully")

