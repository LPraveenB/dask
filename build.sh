docker build --no-cache --build-arg GCR_AUTH_KEY="$1" -t dask-mlpipeline-image:latest .

gcloud auth configure-docker us-west1-docker.pkg.dev

CLOUD_REPOSITORY="us-west1-docker.pkg.dev/inventory-solution-382204/dask-docker"
echo "Push to Container Registry: version taged as latest"
docker tag dask-mlpipeline-image:latest ${CLOUD_REPOSITORY}/dask-mlpipeline-image:latest
docker push ${CLOUD_REPOSITORY}/dask-mlpipeline-image:latest