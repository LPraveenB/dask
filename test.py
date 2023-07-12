import json
from kfp.v2.dsl import component, pipeline
from kfp.v2 import compiler
import google.cloud.aiplatform as aip
from google.cloud.aiplatform import pipeline_jobs

with open('component/training/dask.json', 'r') as f:
    env = json.load(f)


API_ENDPOINT = "{}-aiplatform.googleapis.com".format(env['region'])
PROJECT_ID = env['projectId']
REGION = env['region']
GCS_BUCKET = env['bucket']
SERVICE_ACCOUNT = env['serviceAccount']
CONTAINER_IMAGE = env['containerImage']
PIPELINE_ROOT = f"gs://{GCS_BUCKET}/dask_data/pipeline_root/"
PIPELINE_JSON = "dask_dataframe.json"
MACHINE_TYPE = env['machineType']
WORKERS = env['nWorkers']
project_id = "inventory-solution-382204"
zone = "us-central1-a"
instance_name = "my-instance"
machine_type = "n1-standard-1"
image_project = "ubuntu-os-cloud"
image_family = "ubuntu-minimal-1804-bionic-v20201014"

@component(
    output_component_file="dask_df.yaml",
    packages_to_install=["dask", "distributed", "dask_cloudprovider", "google-auth-httplib2==0.1.0"],
    base_image=CONTAINER_IMAGE
)
def create_instance(
        project_id: str,
        zone: str,
        instance_name: str,
        machine_type: str,
        image_project: str,
        image_family: str
):
    from googleapiclient import discovery
    from google.oauth2 import service_account

    credentials = service_account.Credentials.from_service_account_file(
        'application_default_credentials.json',
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )

    compute = discovery.build('compute', 'v1', credentials=credentials)

    # Create the instance configuration
    config = {
        "name": instance_name,
        "machineType": f"zones/{zone}/machineTypes/{machine_type}",
        "disks": [
            {
                "boot": True,
                "initializeParams": {
                    "sourceImage": f"projects/{image_project}/global/images/{image_family}",
                },
            }
        ],
        "networkInterfaces": [
            {
                "network": "global/networks/default",
                "accessConfigs": [{"type": "ONE_TO_ONE_NAT", "name": "External NAT"}],
            }
        ],
    }

    # Send the request to create the instance
    request = compute.instances().insert(project=project_id, zone=zone, body=config)
    response = request.execute()

    print(f"Creating instance: {instance_name}...")
    # Wait for the operation to complete
    while response.get('status') != 'DONE':
        response = compute.zoneOperations().get(
            project=project_id, zone=zone, operation=response['name']).execute()

    print(f"Instance created: {instance_name}")

# Example usage


# create_instance(project_id, zone, instance_name, machine_type, image_project, image_family)


@pipeline(
    name='daskdf',
    description='Dask Dataframe',
    pipeline_root=PIPELINE_ROOT
)
def dask_pipeline(
        gcs_bucket: str = GCS_BUCKET
):

    dask_dataframe_task = create_instance(project_id, zone, instance_name, machine_type, image_project, image_family)


compiler.Compiler().compile(
    pipeline_func=dask_pipeline,
    package_path=PIPELINE_JSON,
)


aip.init(project=PROJECT_ID, location=REGION)

ai_job = pipeline_jobs.PipelineJob(
    display_name="dataframe-testing",
    template_path=PIPELINE_JSON,
    enable_caching=False
)

ai_job.run()

