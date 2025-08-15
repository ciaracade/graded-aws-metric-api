# Cloud VPC Health and Utilization Metric API

API grades the utilization of subnets in a VPC (Virtrual Private Cloud).

An improved replica of my internship project at Capital One using [LocalStack](https://github.com/localstack/localstack) as a cloud service emulator for AWS services, [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) AWS SDK to manage the EC2 instance and VPC/subnet creation, and practicing the [MVC](https://www.geeksforgeeks.org/software-engineering/mvc-framework-introduction/) framework.

## Getting Started

1. Clone this repo
```
git clone git@github.com:ciaracade/graded-aws-metric-api.git && cd graded-aws-metric-api
```

2. Activate python environment and install dependencies
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create `.env` file in the `src/` directory with the following variables:
```
# AWS Configuration
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
ENDPOINT_URL=http://localhost:4566

# VPC/Subnet creation limits
VPC_MIN=1
VPC_MAX=3
SUBNET_MIN=2
SUBNET_MAX=5

# Utilization ranges
UTIL_LOW=0.05
UTIL_HIGH=0.95

# Random seed (optional)
RAND_SEED=42
```

4. Make sure Docker is running in the background and start LocalStack server:
```
localstack start
```

5. Navigate to the `src` directory and run the seeding script to populate LocalStack with test VPCs:
```
cd src
python aws/seed.py
```

6. Start the Flask API:
```
python app.py
```

7. Use the API locally via Postman or curl:
```
curl http://127.0.0.1:5000 # or whatever endpoint your flask points to
``` 