import dask
from dask.distributed import Client
from dask import dataframe as dd
import os
import sys
import json
import traceback
import subprocess
import papermill as pm
from google.cloud import storage

def get_data_path(base_gcs_path, data_path, location_group):
    if data_path.startswith('gs://'):
        return data_path + '/LOCATION_GROUP='+ location_group +'/*.parquet'
    else:
        return base_gcs_path + '/' + data_path + '/LOCATION_GROUP='+ location_group +'/*.parquet'

def connect_dask(dask_address, num_worker_pools, num_workers, no_worker_threads, memory_limit):
    dask.config.set({"dataframe.shuffle.method": "tasks"})
    if dask_address is not None:
        dask_client = Client(dask_address, timeout=120)
        print('Waiting the scheduler to be connected.')
        if num_worker_pools is not None and num_workers is not None:
            dask_client.wait_for_workers(num_worker_pools*num_workers, 120)
        print('scheduler connected to workers')

    else:
        from dask.distributed import LocalCluster
        dask_cluster = LocalCluster(
            n_workers=num_workers,
            threads_per_worker=no_worker_threads,
            memory_limit=memory_limit)


        dask_client = Client(dask_cluster)
    dask.config.set({"dataframe.shuffle.method": "tasks"})
    return dask_client, dd

def parse_gcs_path(gcs_path):
    gcs_split = gcs_path.split('/')
    bucket_name = gcs_split[2]
    object_path = '/'.join(gcs_split[3:])
    return bucket_name, object_path

def upload_model(model_local_path, model_gcs_path):
    bucket_name, output_path = parse_gcs_path(model_gcs_path)
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    object_name_in_gcs_bucket = bucket.blob(output_path)
    object_name_in_gcs_bucket.upload_from_filename(model_local_path)
    
def download_model(model_local_path, model_gcs_path):
    bucket_name, output_path = parse_gcs_path(model_gcs_path)
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    object_name_in_gcs_bucket = bucket.blob(output_path)
    object_name_in_gcs_bucket.download_to_filename(model_local_path)


def execute_notebook(notebook_path: str, parameters: dict, kernel_name, notebook_bucket, output_path, output_name) -> None:
    """Executes notebook using papermill."""
    try:
        pm.execute_notebook(
            notebook_path,
            output_name + '.ipynb',
            parameters=parameters,
            kernel_name=kernel_name,
            progress_bar=True,
            request_save_on_cell_execute=True)
    finally:
        print('Convert notebook to HTML')
        cmd_to_execute = 'jupyter nbconvert --to=html ' +output_name+ '.ipynb'
        print(f'Running cmd command: {cmd_to_execute}')
        cmd_result = subprocess.run(cmd_to_execute, shell=True, check=True)
        print(f'cmd_result: {cmd_result}')

        client = storage.Client()
        bucket = client.get_bucket(notebook_bucket)
        object_name_in_gcs_bucket = bucket.blob(output_path + '/' + output_name + '.html')
        object_name_in_gcs_bucket.upload_from_filename(output_name + '.html')
    
    

def launch(cmd):
    """ launch dask workers
    """
    return subprocess.check_call(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=True)


def get_chief_ip(cluster_config_dict):
    if 'workerpool0' in cluster_config_dict['cluster']:
      ip_address = cluster_config_dict['cluster']['workerpool0'][0].split(":")[0]
    else:
      # if the job is not distributed, 'chief' will be populated instead of
      # workerpool0.
      ip_address = cluster_config_dict['cluster']['chief'][0].split(":")[0]

    print('The ip address of workerpool 0 is : {}'.format(ip_address))
    return ip_address

def get_chief_port(cluster_config_dict):

    if "open_ports" in cluster_config_dict:
      port = cluster_config_dict['open_ports'][0]
    else:
      # Use any port for the non-distributed job.
      port = 7777
    print("The open port is: {}".format(port))

    return port

def get_cluster_config():
    cluster_config_str = os.environ.get('CLUSTER_SPEC')
    cluster_config_dict  = json.loads(cluster_config_str)
    print(json.dumps(cluster_config_dict, indent=2))
    print('The workerpool type is:', cluster_config_dict['task']['type'], flush=True)
    workerpool_type = cluster_config_dict['task']['type']
    chief_ip = get_chief_ip(cluster_config_dict)
    chief_port = get_chief_port(cluster_config_dict)
    chief_address = "{}:{}".format(chief_ip, chief_port)
    print('current working directory', os.getcwd())
    workerpool1_nodes_len = len(cluster_config_dict['cluster']['workerpool1'])
    print('workerpool1_nodes_len', workerpool1_nodes_len)
    return workerpool_type, chief_ip, chief_port, chief_address, workerpool1_nodes_len

def run_worker(chief_address, num_workers, no_worker_threads, memory_limit):
    print('Running the dask worker.', flush=True)
    client = Client(chief_address, timeout=300)
    print('client: {}.'.format(client), flush=True)
    launch_cmd = "dask-worker {} --nworkers {} --nthreads {} --memory-limit {}".format(chief_address, num_workers, no_worker_threads, memory_limit)
    launch(launch_cmd)
    print('Done with the dask worker.', flush=True)
    
def run_scheduler(chief_address, chief_port):
    print('Running the dask scheduler.', flush=True)
    proc_scheduler = launch('dask-scheduler --dashboard --dashboard-address 8888 --port {} &'.format(chief_port))
    print('Done the dask scheduler.', flush=True)
    
        