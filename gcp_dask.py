import json
from dask_cloudprovider.gcp import GCPCluster
import dask.dataframe as dd
import dask
from google.cloud import storage

with open('dask.json', 'r') as f:
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


country_list = ["Denmark", "China", "Netherlands", "Austria", "Iceland", "Vietnam", "Russia", "Ukraine"]
year_list = ['2010', '2011', '2012']
csv_path = "gs://extracted-bucket-kloud9/dask_data/5m_Sales_Records.csv"
client = storage.Client()
bucket = client.get_bucket(GCS_BUCKET)

# files = bucket.list_blobs(prefix=BLOB)
# csv_path = [file.name for file in files if '.csv' in file.name]
# type(csv_path)
print(csv_path)

df = dd.read_csv(csv_path)

print(df)

df['Order Date'] = dd.to_datetime(df['Order Date'], format='%m/%d/%Y')

df_filtered = df[df['Country'].isin(country_list) & df['Order Date'].isin(year_list)]

units_sold_sum = df_filtered.groupby(['Country', df_filtered['Order Date'].dt.year])['Units Sold'].sum().compute()

print(units_sold_sum)

cluster.close()
