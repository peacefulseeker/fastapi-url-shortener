#!/bin/bash

set -e

echo "Deployment started..."

pnpm run build

TIMESTAMP=$(date +%Y%m%d%H%M)
SHORT_COMMIT=$(git rev-parse --short HEAD)
VERSION=${TIMESTAMP}_${SHORT_COMMIT}

aws s3 sync ../app/static/frontend/ s3://fastapi-url-shortener/fus/v/${VERSION} --acl public-read

echo "Deployment completed with a version uploaded to S3:"
echo "${VERSION}"
