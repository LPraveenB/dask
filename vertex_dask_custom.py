import json
from kfp.v2.dsl import component, pipeline
from kfp.v2 import compiler
from google.cloud import aiplatform as aip

with open('component/training/dask.json', 'r') as f:
    env = json.load(f)

API_ENDPOINT = "{}-aiplatform.googleapis.com".format(env['region'])
PROJECT_ID = env['projectId']
REGION = env['region']
ZONE = env['zone']
GCS_BUCKET = env['bucket']
SERVICE_ACCOUNT = env['serviceAccount']
CONTAINER_IMAGE = env['containerImage']
PIPELINE_ROOT = f"gs://{GCS_BUCKET}/dask_data/pipeline_root/"
PIPELINE_JSON = "dask_dataframe.json"
MACHINE_TYPE = env['machineType']
WORKERS = env['nWorkers']
NETWORK = env['network']
PROJECT_NUMBER = env['projectNumber']
DASK_IMAGE = env['sourceImage']
DOCKER_IMAGE = env['dockerImage']


@component(
    output_component_file="dask_df.yaml",
    packages_to_install=[
        "dask==2023.6.0",
        "distributed==2023.6.0"
    ],
    base_image=CONTAINER_IMAGE
)
def dask_dataframe() -> str:
    import subprocess

    subprocess.run(["python", "gcp_dask.py"])

    return "Dask code executed successfully"


@pipeline(
    name='daskdf',
    description='Dask Dataframe',
    pipeline_root=PIPELINE_ROOT
)
def dask_pipeline():
    dask_dataframe_task = dask_dataframe()


compiler.Compiler().compile(
    pipeline_func=dask_pipeline,
    package_path=PIPELINE_JSON
)

aip.init(project=PROJECT_ID, location=REGION)

ai_job = aip.PipelineJob(
    display_name="dataframe-testing",
    template_path=PIPELINE_JSON,
    enable_caching=False
)

ai_job.run(
    service_account=SERVICE_ACCOUNT,
    network=f"projects/{PROJECT_NUMBER}/global/networks/{NETWORK}"
)
