import json
from dask_cloudprovider.gcp import GCPCluster

with open('component/training/dask.json', 'r') as f:
    env = json.load(f)

PROJECT_ID = env['projectId']
REGION = env['region']
ZONE = env['zone']
GCS_BUCKET = env['bucket']
BLOB = env["blobPrefix"]
SERVICE_ACCOUNT = env['serviceAccount']
CONTAINER_IMAGE = env['containerImage']
PIPELINE_ROOT = f"gs://{GCS_BUCKET}/{BLOB}/pipeline_root/"
PIPELINE_JSON = "dask_dataframe.json"
MACHINE_TYPE = env['machineType']
WORKERS = env['nWorkers']
NETWORK = env['network']
PROJECT_NUMBER = env['projectNumber']
DASK_IMAGE = env['sourceImage']
DOCKER_IMAGE = env['dockerImage']


cluster = GCPCluster(
    projectid=PROJECT_ID,
    zone=ZONE,
    machine_type=MACHINE_TYPE,
    n_workers=WORKERS,
    network=NETWORK
)

cluster.get_logs(scheduler=True, workers=True)


