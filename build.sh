#!/bin/bash

# Save the GCP_SA_KEY secret to a temporary file
echo "$GCP_SA_KEY" > temp_gcp_sa_key.json

# Escape double quotes in the secret JSON and save it to gcp_sa_key.json
cat temp_gcp_sa_key.json | sed 's/"/\\"/g' > /train/gcp_sa_key.json

# Build the Docker image with the GCP_SA_KEY as an argument
docker build --no-cache --build-arg GCP_SA_KEY=$(cat temp_gcp_sa_key.json) -t dask-mlpipeline-image:latest .

# Clean up the temporary file
rm temp_gcp_sa_key.json


gcloud auth configure-docker us-west1-docker.pkg.dev

CLOUD_REPOSITORY="us-west1-docker.pkg.dev/inventory-solution-382204/dask-docker"
echo "Push to Container Registry: version taged as latest"
docker tag dask-mlpipeline-image:latest ${CLOUD_REPOSITORY}/dask-mlpipeline-image:latest
docker push ${CLOUD_REPOSITORY}/dask-mlpipeline-image:latest