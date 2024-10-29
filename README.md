# FastAPI URL Shortener
https://shortenurl.fly.dev/ <br/>
<img src="./demo/preview.gif" alt="preview">

## Stack
- Python 3.11+
- FastAPI
- Poetry
- Docker
- DynamoDB

<img src="./demo/schema.svg" alt="schema" width="500" height="500">


## Backend development locally
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

## Frontend development locally
Given repo is already cloned you're currently in the root directory.
```shell
cd ./frontend
pnpm install
pnpm dev # proxies API calls to dockerized backend (8080 port atm.)
```
