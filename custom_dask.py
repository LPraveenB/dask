import json
from kfp.v2.dsl import component, pipeline
from kfp.v2 import compiler
from google.cloud import aiplatform as aip

with open('dask.json', 'r') as f:
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
def dask_dataframe(
        project_id: str,
        location: str,
        machine_type: str,
        workers: int,
        source_image: str,
        network: str
):

    import json
    from google.cloud import aiplatform

    custom_job = {
        "job_spec": {
            "worker_pool_specs": [
                {
                    "machine_spec": {
                        "machine_type": machine_type,
                        "accelerator_type": aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_K80,
                        "accelerator_count": 1,
                    },
                    "replica_count": 1,
                    "container_spec": {
                        "image_uri": CONTAINER_IMAGE,
                        "command": ['python', 'datafram_task.py'],
                        "args": [],
                    },
                }
            ]
        },
    }
    parent = f"projects/{project_id}/locations/{location}"
    response = client.create_custom_job(parent=parent, custom_job=custom_job)
    print("response:", response)




