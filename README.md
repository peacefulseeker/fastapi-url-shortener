# FastAPI URL Shortener

Built with FastAPI and using DynamoDB for storage,
this project provides a simple and efficient solution
for managing and redirecting shortened links.

## Stack
- Python 3.11+
- FastAPI
- Poetry
- Docker
- DynamoDB

<img src="./demo/schema.svg" alt="schema" width="500" height="500">

# Live + Demo
See live: https://shortenurl.fly.dev/ <br/>
Demo: <br/>
<img src="./demo/preview.gif" alt="preview">



## Local development
1. Clone the repository:
```shell
git clone git@github.com:peacefulseeker/fastapi-url-shortener.git ./local-project-dir
cd ./local-project-dir
```

2. Install dependencies:
```shell
poetry install
```

3. Run the application in dev mode:
```shell
make dev
```

3.1 Run the dockerized application in dev mode:
```shell
docker-compose up -d --build
```
