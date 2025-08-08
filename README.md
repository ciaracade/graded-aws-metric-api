# Graded AWS Metrics API

An improved replica of my internship project at Capital One using [LocalStack](https://github.com/localstack/localstack) for AWS testing and practicing the [MVC](https://www.geeksforgeeks.org/software-engineering/mvc-framework-introduction/) framework.

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

3. Make sure docker is running in the background and strat LocalStack server.
```
localstack start
```

4. Run `seed.py`.
```
python run db/seed.py
```

5. Use locally api via postman or whatever you like. 