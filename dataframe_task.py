import json
import dask.dataframe as dd
from google.cloud import storage

with open('component/training/dask.json', 'r') as f:
    env = json.load(f)

GCS_BUCKET = env['bucket']
BLOB = env["blobPrefix"]
csv_path = "gs://extracted-bucket-kloud9/dask_data/5m_Sales_Records.csv"
country_list = ["Denmark", "China", "Netherlands", "Austria", "Iceland", "Vietnam", "Russia", "Ukraine"]
year_list = ['2010', '2011', '2012']

client = storage.Client()
bucket = client.get_bucket(GCS_BUCKET)

df = dd.read_csv(csv_path)
df['Order Date'] = dd.to_datetime(df['Order Date'], format='%m/%d/%Y')
df_filtered = df[df['Country'].isin(country_list) & df['Order Date'].isin(year_list)]
units_sold_sum = df_filtered.groupby(['Country', df_filtered['Order Date'].dt.year])['Units Sold'].sum().compute()
print(units_sold_sum)

