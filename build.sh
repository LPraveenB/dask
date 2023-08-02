#!/bin/bash
set -e

# Copy secret to a temporary file
printf '%s' "$1" > temp_gcp_sa_key.json

# Escape double quotes and save to /train/gcp_sa_key.json
cat temp_gcp_sa_key.json | sed 's/"/\\"/g' > /train/gcp_sa_key.json

# Build Docker image
docker build --no-cache -t dask-mlpipeline-image:latest .

# Authenticate Docker to Google Container Registry
gcloud auth configure-docker us-west1-docker.pkg.dev

# Push Docker image to Google Container Registry
CLOUD_REPOSITORY="us-west1-docker.pkg.dev/inventory-solution-382204/dask-docker"
echo "Push to Container Registry: version tagged as latest"
docker tag dask-mlpipeline-image:latest ${CLOUD_REPOSITORY}/dask-mlpipeline-image:latest
docker push ${CLOUD_REPOSITORY}/dask-mlpipeline-image:latest