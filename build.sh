docker build --no-cache -t dask-mlpipeline-image:latest .

gcloud auth configure-docker us-west1-docker.pkg.dev

CLOUD_REPOSITORY="us-west1-docker.pkg.dev/inventory-solution-382204/dask-docker"
echo "Push to Container Registry: version taged as latest"
docker tag dask-mlpipeline-image:latest ${CLOUD_REPOSITORY}/dask-mlpipeline-image:latest
docker push ${CLOUD_REPOSITORY}/dask-mlpipeline-image:latest



us-docker.pkg.dev/inventory-solution-382204/dask-docker