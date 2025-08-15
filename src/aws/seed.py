#!/usr/bin/env python3
"""
Seed LocalStack with VPCs and subnets at various utilization levels.
Run this script once to populate the environment for testing.
"""

import logging
from config import AWSConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Seed LocalStack with test VPCs and subnets"""
    logger.info("Starting LocalStack seeding...")

    try:
        # Create AWS config and seed the cloud
        aws_config = AWSConfig()
        aws_config.seed_cloud(aws_config.ec2)
        logger.info("Seeding completed successfully!")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise


if __name__ == "__main__":
    main()
