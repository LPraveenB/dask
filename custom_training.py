import os
import sys
import argparse
import json
import kfp
import kfp.dsl as dsl
from kfp.v2.dsl import component, Output, HTML
from pathlib import Path
import datetime
import google.cloud.aiplatform as vertex_ai
from kfp.registry import RegistryClient

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = 'dollar-tree-project-369709'
REGION = 'us-west1'
PIPELINE_ROOT = 'gs://user-bucket-dollar-tree/darshan/vertex_pipeline'
BUCKET_NAME = 'extracted-bucket-dollar-tree'
BASE_PATH = 'Ramalingam/phase2/3M/auditonly/vertex_pipeline'


@component(
    base_image="python:3.7",
    packages_to_install=["google-cloud-aiplatform==1.24.1"],
    output_component_file=str(Path(__file__).with_suffix(".yaml")),
)
def custom_eval_job(
        project_id: str,
        project_location: str,
        container_uri: str,
        staging_bucket: str,
        job_name: str,
        job_suffix: str,
        replica_count: int,
        master_machine_type: str,
        worker_machine_type: str,
        run_type: str,
        memory_limit: str,
        base_gcs_path: str,
        num_workers: int,
        no_worker_threads: int,
        data_split_path: str,
        fs_eval_path: str,
        location_group: str):
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
                    '--run_type', run_type,
                    '--memory_limit', memory_limit,
                    '--base_gcs_path', base_gcs_path,
                    '--num_workers', str(num_workers),
                    '--no_worker_threads', str(no_worker_threads),
                    '--data_split_path', data_split_path,
                    '--fs_eval_path', fs_eval_path,
                    '--location_group', location_group,
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
                    '--memory_limit', memory_limit,
                    '--num_workers', str(num_workers),
                    '--no_worker_threads', str(no_worker_threads)
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


@component(
    base_image="python:3.7",
    packages_to_install=["google-cloud-aiplatform==1.24.1"],
    output_component_file=str(Path(__file__).with_suffix(".yaml")),
)
def custom_train_job(
        project_id: str,
        project_location: str,
        container_uri: str,
        staging_bucket: str,
        job_name: str,
        job_suffix: str,
        replica_count: int,
        master_machine_type: str,
        worker_machine_type: str,
        run_type: str,
        train_start_date: str,
        memory_limit: str,
        base_gcs_path: str,
        num_workers: int,
        no_worker_threads: int,
        data_split_path: str,
        location_group: str,
        num_booster: int,
        max_depth: int,
        min_child_weight: int,
        learning_rate: float,
        feature_count: int,
        scale_pos_multiply_factor: float,
        eval_metric: str):
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
                    '--run_type', run_type,
                    '--train_start_date', train_start_date,
                    '--memory_limit', memory_limit,
                    '--base_gcs_path', base_gcs_path,
                    '--num_workers', str(num_workers),
                    '--no_worker_threads', str(no_worker_threads),
                    '--data_split_path', data_split_path,
                    '--location_group', location_group,
                    '--num_booster', str(num_booster),
                    '--min_train_days', '270',
                    '--max_depth', str(max_depth),
                    '--min_child_weight', str(min_child_weight),
                    '--learning_rate', str(learning_rate),
                    '--feature_count', str(feature_count),
                    '--scale_pos_multiply_factor', str(scale_pos_multiply_factor),
                    '--eval_metric', eval_metric,
                    '--steps', 'train'
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
                    '--memory_limit', memory_limit,
                    '--num_workers', str(num_workers),
                    '--no_worker_threads', str(no_worker_threads)
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


"""@component
def html_notebook_visualization(
        html_artifact: Output[HTML],
        bucket: str,
        base_path: str,
        job_name: str,
        job_suffix: str,
        path_suffix: str,
        project_id: str) -> None:
    import os
    from google.cloud import storage
    gcs_client = storage.Client(project_id)
    full_path_without_bucket = base_path + '/' + job_name + '_' + job_suffix + '/' + path_suffix
    gcs_bucket = gcs_client.get_bucket(bucket)
    blob = gcs_bucket.blob(full_path_without_bucket)
    html_content = blob.download_as_text()
    with open(html_artifact.path, 'w') as f:
        f.write(html_content)"""


@dsl.pipeline(
    name='model-training',
    description='Model Training',
    pipeline_root=PIPELINE_ROOT)
def pipeline(
        run_name: str = '3M_TESTRUN1',
        run_type: str = 'all',
        train_start_date: str = '2021-08-01',
        train_memory_limit: str = '512GB',
        eval_memory_limit: str = '512GB',
        train_num_workers: int = 47,
        train_no_worker_threads: int = 2,
        eval_num_workers: int = 47,
        eval_no_worker_threads: int = 2,
        fs_eval_path: str = 'gs://extracted-bucket-dollar-tree/Ramalingam/phase2/3M/auditonly/feature_store_3m_eval.parquet',
        data_split_path: str = 'gs://extracted-bucket-dollar-tree/Ramalingam/phase2/3M/auditonly/vertex_training_datasplit/feature_store_3m_train-datasplit/data_split.parquet',
        location_group: str = 'ALL',
        num_booster: int = 50,
        max_depth: int = 6,
        min_child_weight: int = 3,
        learning_rate: float = 0.1,
        feature_count: int = 20,
        scale_pos_multiply_factor: float = 1,
        eval_metric: str = 'logloss',
        train_replica_count: int = 3,
        train_master_machine_type: str = "n1-highmem-32",
        train_worker_machine_type: str = "n1-highmem-96",
        eval_replica_count: int = 1,
        eval_master_machine_type: str = "n1-highmem-32",
        eval_worker_machine_type: str = "n1-highmem-96"):
    run_name_suffix = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    run_name_suffix = str(run_name_suffix)
    run_name_suffix = run_name_suffix[0:8] + '_' + run_name_suffix[8:14] if len(
        run_name_suffix) and run_name_suffix.isdigit() else run_name_suffix

    train_xgb_task = custom_train_job(
        project_id=PROJECT_ID,
        project_location=REGION,
        container_uri='us-west1-docker.pkg.dev/dollar-tree-project-369709/fd-distributed-training/xgb-dask:v12',
        staging_bucket='user-bucket-dollar-tree',
        job_name=run_name,
        job_suffix='Training' + '_' + run_name_suffix,
        replica_count=train_replica_count,
        master_machine_type=train_master_machine_type,
        worker_machine_type=train_worker_machine_type,
        run_type=run_type,
        train_start_date=train_start_date,
        memory_limit=train_memory_limit,
        base_gcs_path='gs://' + BUCKET_NAME + '/' + BASE_PATH,
        num_workers=train_num_workers,
        no_worker_threads=train_no_worker_threads,
        data_split_path=data_split_path,
        location_group=location_group,
        num_booster=num_booster,
        max_depth=max_depth,
        min_child_weight=min_child_weight,
        learning_rate=learning_rate,
        feature_count=feature_count,
        scale_pos_multiply_factor=scale_pos_multiply_factor,
        eval_metric=eval_metric)

    """html_notebook_visualization(BUCKET_NAME, BASE_PATH, run_name, 'Training' + '_' + run_name_suffix,
                                'train_notebook/train_output.html', PROJECT_ID).after(train_xgb_task)"""

    eval_xgb_task = custom_eval_job(
        project_id=PROJECT_ID,
        project_location=REGION,
        container_uri='us-west1-docker.pkg.dev/dollar-tree-project-369709/fd-dask-docker/dask-mlpipeline-image:latest',
        staging_bucket='user-bucket-dollar-tree',
        job_name=run_name,
        job_suffix='Training' + '_' + run_name_suffix,
        replica_count=eval_replica_count,
        master_machine_type=eval_master_machine_type,
        worker_machine_type=eval_worker_machine_type,
        run_type=run_type,
        memory_limit=eval_memory_limit,
        base_gcs_path='gs://' + BUCKET_NAME + '/' + BASE_PATH,
        num_workers=eval_num_workers,
        no_worker_threads=eval_no_worker_threads,
        data_split_path=data_split_path,
        fs_eval_path=fs_eval_path,
        location_group=location_group).after(train_xgb_task)

    """html_notebook_visualization(BUCKET_NAME, BASE_PATH, run_name, 'Training' + '_' + run_name_suffix,
                                'eval_notebook/eval_output.html', PROJECT_ID).after(eval_xgb_task)"""

    # html_notebook_visualization(BUCKET_NAME, BASE_PATH, run_name, 'Training' + '_' + run_name_suffix, 'metric_notebook/metric_output.html', PROJECT_ID).after(eval_xgb_task)


if __name__ == '__main__':
    # try:
    versioned_pipeline_file = 'pipeline.json'
    logger.info('--- Compile pipeline as V2 ---')
    kfp.compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path=versioned_pipeline_file)


    kfp.compiler.Compiler().compile(
    pipeline_func=pipeline, package_path="pipeline_template.yaml"
    )

    vertex_ai.init(project=PROJECT_ID, location=REGION, staging_bucket=PIPELINE_ROOT)

    client = RegistryClient(
        host=f"https://us-west1-kfp.pkg.dev/dollar-tree-project-369709/ml-run-kfp-repo"
    )

    templateName, versionName = client.upload_pipeline(
        file_name="pipeline_template.yaml",
        tags=["v1", "latest"],
        extra_headers={"description": "This is a pipeline"},
    )

    GCS_BUCKET = PIPELINE_ROOT

    job = vertex_ai.PipelineJob(
        display_name="pipeline",
        template_path=f"https://us-west1-kfp.pkg.dev/dollar-tree-project-369709/ml-run-kfp-repo/model-training/" + versionName,
    )

    job.submit()
    """client = kfp.Client()
    experiment = client.create_experiment('xgboost-dask')

    run_name = pipeline.__name__ + ' run'

    arguments = {"model_path": "mnist_model",
                 "bucket": GCS_BUCKET}

    run_result = client.run_pipeline(
        experiment_id=experiment.id,
        job_name=run_name,
        pipeline_package_path=versioned_pipeline_file,
        params=arguments)"""
    # except Exception as e:
    #    logger.error(f'Error occured during pipeline compilation: {e}')