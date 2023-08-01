import datetime
import json
from kfp.dsl import component, pipeline
from kfp.v2 import compiler
from pathlib import Path
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
STAGING_BUCKET = env['stagingBucket']
PIPELINE_JSON = "dask_dataframe.json"
MASTER_MACHINE_TYPE = env['masterMachineType']
WORKER_MACHINE_TYPE = env['workerMachineType']
WORKERS = env['nWorkers']
NETWORK = env['network']
PROJECT_NUMBER = env['projectNumber']
DASK_IMAGE = env['sourceImage']
DOCKER_IMAGE = env['dockerImage']


@component(
    base_image="python:3.7",
    packages_to_install=["google-cloud-aiplatform==1.24.1"],
    output_component_file=str(Path(__file__).with_suffix(".yaml")),
)
def dask_dataframe(
        project_id: str,
        project_location: str,
        container_uri: str,
        staging_bucket: str,
        job_name: str,
        job_suffix: str,
        replica_count: int,
        master_machine_type: str,
        worker_machine_type: str,
        num_workers: int,
):
    """Run a custom training job using a training script.
    """
    import json
    import logging
    import os.path
    import time
    import google.cloud.aiplatform as aip

    worker_pool_specs = [
        {
            "machine_spec": {
                "machine_type": master_machine_type,
            },
            "replica_count": 1,
            "container_spec": {
                "image_uri": container_uri,
                "command": ['bash', 'entrypoint.sh'],
                "args": [
                    '--run_name', job_name + '_' + job_suffix,
                    '--num_workers', str(num_workers),
                    '--steps', 'evaluate'
                ],
            },
        },
        {
            "machine_spec": {
                "machine_type": worker_machine_type,
            },
            "replica_count": replica_count,
            "container_spec": {
                "image_uri": container_uri,
                "command": ['bash', 'entrypoint.sh'],
                "args": [
                    '--num_workers', str(num_workers),
                ],
            },
        }
    ]

    my_job = aip.CustomJob(
        display_name=job_name + '_' + job_suffix,
        worker_pool_specs=worker_pool_specs,
        staging_bucket=staging_bucket,
        project=project_id,
        location=project_location
    )

    my_job.run()


@pipeline(
    name='daskdf',
    description='Dask Dataframe',
    pipeline_root=PIPELINE_ROOT
)
def dask_pipeline(
        run_name: str = "dask-testing",
        train_master_machine_type: str = "n1-highmem-2",
        train_worker_machine_type: str = "n1-highmem-4",
        train_replica_count: int = 3,
        train_num_workers: int = 2

):
    run_name_suffix = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    run_name_suffix = str(run_name_suffix)
    run_name_suffix = run_name_suffix[0:8] + '_' + run_name_suffix[8:14] if len(
        run_name_suffix) and run_name_suffix.isdigit() else run_name_suffix
    dask_dataframe_task = dask_dataframe(
        project_id=PROJECT_ID,
        project_location=REGION,
        container_uri=CONTAINER_IMAGE,
        staging_bucket=STAGING_BUCKET,
        job_name=run_name,
        job_suffix= 'Dask' + '-' + run_name_suffix,
        master_machine_type=train_master_machine_type,
        worker_machine_type=train_worker_machine_type,
        replica_count = train_replica_count,
        num_workers = train_num_workers
    )


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
