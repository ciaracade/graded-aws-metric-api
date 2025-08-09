# Graded AWS Metrics API

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

3. Create `.env` file and populate for your AWS account.
```
AWS_ACCESS_KEY_ID = 
AWS_SECRET_ACCESS_KEY = 
ENDPOINT_URL = 
```

If using LocalStack:
```
ENDPOINT_URL='http://localhost:4566',
AWS_ACCESS_KEY_ID='test',
AWS_SECRET_ACCESS_KEY='test'
```

3. Make sure docker is running in the background and strat LocalStack server.
```
localstack start
```

4. Run `seed.py`.
```
python run db/seed.py
```

5. Use locally api via postman or whatever you like. 