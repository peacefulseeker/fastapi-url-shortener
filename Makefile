test = poetry run pytest --capture=fd --verbosity=0

# Include environment variables from .env file if it exists
ifneq (,$(wildcard ./app/.env))
    include ./app/.env
    export
endif

# production app builds for local testing
IMAGE_NAME=urlshortener
IMAGE_TAG=latest
IMAGE_NETWORK=url-shortener-network

docker-build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

docker-run:
	docker run --network $(IMAGE_NETWORK) \
		-e DDB_ENDPOINT_URL=http://ddb:8000 \
		-p 8080:8080 \
		$(IMAGE_NAME):$(IMAGE_TAG)

docker-exec:
	docker exec -it $$(docker ps -q --filter ancestor=$(IMAGE_NAME):$(IMAGE_TAG)) /bin/bash


# development
dev:
	fastapi dev app/main.py --port 8000 --host 0.0.0.0

prod:
	DEBUG=false fastapi run app/main.py --port 8000 --host 0.0.0.0

lint:
	poetry run ruff format --check app tests
	poetry run ruff check app tests
	poetry run toml-sort pyproject.toml --check

fmt:
	poetry run ruff format app tests
	poetry run ruff check --select I --fix  # sort imports
	poetry run toml-sort pyproject.toml

test:
	${test}

testparallel:
	${test} -n auto

testwithcoverage:
	$(test) \
		--cov=app \
		--cov-report=term-missing:skip-covered \
		--cov-fail-under=90

check-local-env:
	@echo "Environment variables:"
	@echo "======================"
	@echo "AWS_ACCESS_KEY_ID: $${AWS_ACCESS_KEY_ID:-not set}"
	@echo "AWS_SECRET_ACCESS_KEY: $${AWS_SECRET_ACCESS_KEY:-not set (length only)}"
	@echo "AWS_REGION: $${AWS_REGION:-not set}"
	@echo "DDB_TABLE_NAME: $(DDB_TABLE_NAME)"
	@echo "DDB_ENDPOINT_URL: $${DDB_ENDPOINT_URL:-not set}"
	@echo "======================"

create-ddb-table-local:
	aws dynamodb create-table \
		--table-name $$DDB_TABLE_NAME \
		--attribute-definitions \
			AttributeName=ShortPath,AttributeType=S \
			AttributeName=FullUrl,AttributeType=S \
		--key-schema \
			AttributeName=ShortPath,KeyType=HASH \
		--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
		--global-secondary-indexes \
			"[{\"IndexName\": \"FullUrl-index\", \
			\"KeySchema\": [{\"AttributeName\": \"FullUrl\", \"KeyType\": \"HASH\"}], \
			\"Projection\": {\"ProjectionType\": \"INCLUDE\", \"NonKeyAttributes\": [\"ExpiresAt\"]}, \
			\"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}}]" \
		--endpoint-url $$DDB_ENDPOINT_URL

remove-ddb-table-local:
	aws dynamodb delete-table --table-name $$DDB_TABLE_NAME --endpoint-url $$DDB_ENDPOINT_URL

buildfrontend:
	cd frontend && pnpm run build

servefrontend:
	cd frontend && pnpm dev

deployfrontend:
	cd frontend && sh ./deploy_assets_version_to_s3.sh

