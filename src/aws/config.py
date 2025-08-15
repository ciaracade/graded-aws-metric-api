"""
Generates AWS VPCs and subnets with different levels of utilization
via LocalStack
"""

import boto3
import ipaddress
from botocore.config import Config
from dotenv import load_dotenv
import logging
import os, random, math
from typing import Tuple

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
    
    
    def seed_cloud(self, ec2: boto3.client) -> None:
        """ Seeds AWS EC2 instance with VPCs of various subnet utilizations """
        self.check_ranges()

        # Create randoms for VPC and subnet ranges
        vpc_count = random.randint(VPC_MIN, VPC_MAX)
        logger.info(f"Seeding {vpc_count} VPCs...")

        # Create VPCs with subnets
        for vpc_idx in range(1, vpc_count+1):
            logger.info(f"Creating VPC #{vpc_idx}...")
            try:
                # Create VPC
                vpc_cidr = self.random_vpc_cidr()
                vpc_response = ec2.create_vpc(CidrBlock=vpc_cidr)
                vpc_id = vpc_response["Vpc"]["VpcId"]
                self.tag(ec2, vpc_id, f"seed-vpc-{vpc_idx}")
                logger.info(f"Created VPC #{vpc_idx}: {vpc_id} ({vpc_cidr})")

                # Create security group for this VPC
                sg_id = self.ensure_sg(ec2, vpc_id, f"seed-sg-{vpc_idx}")
                
                # Create subnets in this VPC
                subnet_count = random.randint(SUBNET_MIN, SUBNET_MAX)
                for subnet_idx in range(1, subnet_count+1):
                    logger.info(f"Creating subnet #{subnet_idx} in VPC #{vpc_idx}...")
                    try:
                        # Create subnet
                        subnet_cidr = self.nth_subnet_cidr(vpc_cidr, subnet_idx)
                        subnet_response = ec2.create_subnet(VpcId=vpc_id, CidrBlock=subnet_cidr)
                        subnet_id = subnet_response["Subnet"]["SubnetId"]
                        self.tag(ec2, subnet_id, f"seed-subnet-{vpc_idx}-{subnet_idx}")
                        
                        # Fill subnet to random utilization
                        target_util = random.uniform(UTIL_LOW, UTIL_HIGH)
                        used, cap, actual_util = self.fill_subnet_to_utilization(
                            ec2, subnet_id, sg_id, subnet_cidr, target_util
                        )
                        logger.info(f"Created subnet #{subnet_idx}: {subnet_id} ({subnet_cidr}) - {used}/{cap} IPs ({actual_util}%)")
                        
                    except Exception as e:
                        logger.error(f"Failed to create subnet #{subnet_idx} in VPC #{vpc_idx}: {e}")
                        raise
                        
                logger.info(f"Completed VPC #{vpc_idx} with {subnet_count} subnets")
                
            except Exception as e:
                logger.error(f"Failed to create VPC #{vpc_idx}: {e}")
                raise
                
        logger.info(f"Cloud seeding completed: {vpc_count} VPCs created") 
     
    def create_vpc(self) -> str:
        """ Creates VPC """

        
    def create_subnet(self) -> str:
        """ Creates subnet """

    # del: for model
    def get_vpc(self) -> dict:
        """ Gets VPC """
    
    # del: for model
    def get_subnet(self) -> dict:
        """ Gets subnet """
    
    def check_ranges(self) -> None:
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

    # Hepers for seeding

    def tag(self, ec2: boto3.client, resource_id: str, name: str) -> None:
        ec2.create_tags(Resources=[resource_id], Tags=[{"Key": "Name", "Value": name}])

    def random_vpc_cidr(self) -> str:
        # 10.X.0.0/16 (overlap is fine for LocalStack demos)
        x = random.randint(10, 200)
        return f"10.{x}.0.0/16"

    def nth_subnet_cidr(self, vpc_cidr: str, n: int) -> str:
        # /24s inside the /16 -> 10.X.n.0/24
        net = ipaddress.ip_network(vpc_cidr)
        o = str(net.network_address).split(".")
        return f"{o[0]}.{o[1]}.{n}.0/24"

    def subnet_capacity(self, cidr: str) -> int:
        # AWS usable IPs per subnet = total - 5 (reserved)
        return max(ipaddress.ip_network(cidr).num_addresses - 5, 0)

    def usable_ips(self, cidr: str) -> list[str]:
        # Skip first 3 hosts + last host to mimic AWS reserves
        hosts = list(ipaddress.ip_network(cidr).hosts())
        return [str(ip) for ip in hosts[3:-1]] if len(hosts) >= 5 else []

    def ensure_sg(self, ec2: boto3.client, vpc_id: str, name: str) -> str:
        sg_id = ec2.create_security_group(GroupName=name, Description=name, VpcId=vpc_id)["GroupId"]
        try:
            ec2.authorize_security_group_egress(
                GroupId=sg_id,
                IpPermissions=[{"IpProtocol": "-1", "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}]
            )
        except Exception:
            pass
        return sg_id

    def fill_subnet_to_utilization(self, ec2: boto3.client, subnet_id: str, sg_id: str, cidr: str, target_util: float) -> Tuple[int, int, float]:
        cap = self.subnet_capacity(cidr)
        if cap <= 0:
            return (0, 0, 0.0)
        target_used = min(math.floor(cap * target_util), cap)
        if target_used <= 0:
            return (0, cap, 0.0)

        ips = self.usable_ips(cidr)
        used = 0
        i = 0
        while used < target_used and i < len(ips):
            batch = min(20, target_used - used)  # 1 primary + up to 19 secondary IPs
            primary = ips[i]
            secondaries = [{"PrivateIpAddress": ip, "Primary": False} for ip in ips[i+1:i+batch]]
            eni = ec2.create_network_interface(
                SubnetId=subnet_id,
                Groups=[sg_id],
                PrivateIpAddress=primary,
                PrivateIpAddresses=secondaries,
                Description="seed",
            )["NetworkInterface"]
            self.tag(ec2, eni["NetworkInterfaceId"], "seed")
            used += batch
            i += batch

        return (used, cap, round(100 * used / cap, 2))
