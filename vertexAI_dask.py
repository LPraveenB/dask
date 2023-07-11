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
) -> str:
    import json
    import dask.dataframe as dd
    from dask_cloudprovider.gcp import GCPCluster
    import os

    with open('dask.json', 'r') as o:
        config = json.load(o)

    cluster = GCPCluster(
        projectid=project_id,
        zone=location,
        machine_type=machine_type,
        n_workers=workers,
        source_image=source_image,
        network=network,

    )

    cluster.get_logs()

    country_list = config['countryList']
    print(country_list)
    year_list = config['yearList']
    print(year_list)
    gcs_bucket = os.getenv('GCS_BUCKET')
    csv_path = "gs://extracted-bucket-kloud9/dask_data/5m_Sales_Records.csv"
    df = dd.read_csv(csv_path)
    df['Order Date'] = dd.to_datetime(df['Order Date'], format='%m/%d/%Y')
    df_filtered = df[df['Country'].isin(country_list) & df['Order Date'].isin(year_list)]
    print(df_filtered)
    units_sold_sum = df_filtered.groupby(['Country', df_filtered['Order Date'].dt.year])['Units Sold'].sum().compute()

    print(units_sold_sum)

    cluster.close()

    return "Dataframe job successful and Cluster Closed "


@pipeline(
    name='daskdf',
    description='Dask Dataframe',
    pipeline_root=PIPELINE_ROOT
)
def dask_pipeline(
        project_id: str = PROJECT_ID,
        location: str = ZONE,
        machine_type: str = MACHINE_TYPE,
        workers: int = WORKERS,
        source_image: str = DASK_IMAGE,
        network: str = NETWORK
):
    dask_dataframe_task = dask_dataframe(
        project_id,
        location,
        machine_type,
        workers,
        source_image,
        network
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
