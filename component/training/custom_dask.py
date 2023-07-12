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
MASTER_MACHINE_TYPE = env['masterMachineType']
WORKER_MACHINE_TYPE = env['workerMachineType']
WORKERS = env['nWorkers']
NETWORK = env['network']
PROJECT_NUMBER = env['projectNumber']
DASK_IMAGE = env['sourceImage']
DOCKER_IMAGE = env['dockerImage']
STAGING_BUCKET = env['stagingBucket']


@component(
    output_component_file="../../dask_df.yaml",
    packages_to_install=["google-cloud-aiplatform"],
    base_image=CONTAINER_IMAGE
)
def dask_dataframe(
        project_id: str,
        project_location: str,
        container_uri: str,
        staging_bucket: str,
        job_name: str,
        job_suffix: str,
        master_machine_type: str,
        worker_machine_type: str,
        num_workers: int,
        replica_count: int
):

    import json
    import google.cloud.aiplatform as aip

    worker_pool_specs = [
        {
            "machine_spec": {
                "machine_type": master_machine_type,
            },
            "replica_count": replica_count,
            "container_spec": {
                "image_uri": container_uri,
                "command": ['python', 'dataframe_task.py'],
                "args": [
                    '--run_name', job_name + '_' + job_suffix,
                    '--num_workers', str(num_workers)
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
                "command": ['python', 'dataframe_task.py'],
                "args": [
                    '--num_workers', str(num_workers)
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
        project_id: str = PROJECT_ID,
        project_location: str = REGION,
        container_uri: str = CONTAINER_IMAGE,
        staging_bucket: str = STAGING_BUCKET,
        job_name: str = "Dask-DF",
        job_suffix: str = "Test",
        master_machine_type: str = MASTER_MACHINE_TYPE,
        worker_machine_type: str = WORKER_MACHINE_TYPE,
        replica_count: int = 1,
        num_workers: int = WORKERS
):
    dask_dataframe_task = dask_dataframe(
        project_id,
        project_location,
        container_uri,
        staging_bucket,
        job_name,
        job_suffix,
        master_machine_type,
        worker_machine_type,
        replica_count,
        num_workers
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




