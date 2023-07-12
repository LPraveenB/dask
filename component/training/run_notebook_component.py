
import argparse
import datetime
import generic_utils


def main_scheduler(chief_address, chief_port, workerpool_nodes_len, args=None):
    print("args", args)
    parser = argparse.ArgumentParser(description='Running DS Ready FS Subset')
    
    parser.add_argument(
        '--run_name',
        dest='run_name',
        type=str,
        required=True,
        help='run_name')
    
    parser.add_argument(
        '--run_type',
        dest='run_type',
        type=str,
        required=True,
        help='run_type')
    
    
    
    parser.add_argument(
        '--max_depth',
        dest='max_depth',
        type=int,
        required=False,
        help='max_depth')
    
    parser.add_argument(
        '--min_child_weight',
        dest='min_child_weight',
        type=int,
        required=False,
        help='min_child_weight')
    
    parser.add_argument(
        '--learning_rate',
        dest='learning_rate',
        type=float,
        required=False,
        help='learning_rate')
    
    parser.add_argument(
        '--min_train_days',
        dest='min_train_days',
        type=int,
        required=False,
        help='min_train_days')
    
    parser.add_argument(
        '--train_start_date',
        dest='train_start_date',
        type=str,
        required=False,
        help='train_start_date')
    
    parser.add_argument(
        '--kernel_name',
        dest='kernel_name',
        type=str,
        required=True,
        help='kernel_name')
    
    parser.add_argument(
        '--num_worker_pools',
        dest='num_worker_pools',
        type=int,
        required=False,
        help='num_worker_pools')
    
    parser.add_argument(
        '--location_group',
        dest='location_group',
        type=str,
        required=True,
        help='location_group')
    
    parser.add_argument(
        '--fs_path',
        dest='fs_path',
        type=str,
        required=False,
        help='fs_path')
    
    parser.add_argument(
        '--fs_eval_path',
        dest='fs_eval_path',
        type=str,
        required=False,
        help='fs_eval_path')
    
    
    parser.add_argument(
        '--data_split_path',
        dest='data_split_path',
        type=str,
        required=False,
        help='data_split_path')
    
    parser.add_argument(
        '--num_workers',
        dest='num_workers',
        type=int,
        required=False,
        help='num_workers')
    
    parser.add_argument(
        '--no_data_chunks',
        dest='no_data_chunks',
        type=int,
        required=False,
        help='no_data_chunks')
    
    parser.add_argument(
        '--base_gcs_path',
        dest='base_gcs_path',
        type=str,
        required=False,
        help='base_gcs_path')
    
    parser.add_argument(
        '--no_worker_threads',
        dest='no_worker_threads',
        type=int,
        required=False,
        help='no_worker_threads')
    
    parser.add_argument(
        '--memory_limit',
        dest='memory_limit',
        type=str,
        required=True,
        help='memory_limit')
    
    parser.add_argument(
        '--num_booster',
        dest='num_booster',
        type=int,
        required=False,
        help='num_booster')
    
    parser.add_argument(
        '--feature_count',
        dest='feature_count',
        type=int,
        required=False,
        help='feature_count')
    
    parser.add_argument(
        '--scale_pos_multiply_factor',
        dest='scale_pos_multiply_factor',
        type=float,
        required=False,
        help='scale_pos_multiply_factor')
    
    
    parser.add_argument(
        '--eval_metric',
        dest='eval_metric',
        type=str,
        required=False,
        help='eval_metric')
    
    
    
    
    parser.add_argument(
        '--steps',
        dest='steps',
        type=str,
        required=True,
        help='steps')
    
    
    
    args = parser.parse_args(args)
    
    run_name = args.run_name
    if run_name is None or run_name.strip() == '':
        run_name = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        run_name = str(run_name)
        run_name = run_name[0:8] + '_' + run_name[8:14] if len(run_name) and run_name.isdigit() else run_name
    
    if args.no_data_chunks is None:
        no_data_chunks = workerpool_nodes_len * args.num_workers * args.no_worker_threads
        
    notebook_parameters = {}
    notebook_parameters['memory_limit_env'] = args.memory_limit
    notebook_parameters['no_worker_threads_env'] = args.no_worker_threads
    notebook_parameters['base_gcs_path_env'] = args.base_gcs_path
    notebook_parameters['no_data_chunks_env'] = no_data_chunks
    notebook_parameters['num_workers_env'] = args.num_workers
    notebook_parameters['run_name_env'] = run_name
    notebook_parameters['fs_eval_path_env'] = args.fs_eval_path
    notebook_parameters['location_group_env'] = args.location_group
    notebook_parameters['num_worker_pools'] = args.num_worker_pools
    notebook_parameters['dask_address'] = chief_address
    notebook_parameters['min_train_days_env'] = args.min_train_days
    notebook_parameters['train_start_date_env'] = args.train_start_date
    notebook_parameters['data_split_path_env'] = args.data_split_path
    notebook_parameters['run_type'] = args.run_type
    
    
    
    
    
    
    
    print(f'kernel_name: {args.kernel_name}')
    print(f'memory_limit: {args.memory_limit}')
    print(f'base_gcs_path: {args.base_gcs_path}')
    print(f'no_data_chunks: {args.no_data_chunks}')
    print(f'num_workers: {args.num_workers}')
    print(f'run_name: {run_name}')
    print(f'fs_eval_path: {args.fs_eval_path}')
    print(f'location_group: {args.location_group}')
    print(f'no_worker_threads: {args.no_worker_threads}')
    print(f'num_worker_pools: {args.num_worker_pools}')
    print(f'num_booster: {args.num_booster}')
    
    print(f'max_depth: {args.max_depth}')
    print(f'min_child_weight: {args.min_child_weight}')
    print(f'learning_rate: {args.learning_rate}')
    print(f'min_train_days: {args.min_train_days}')
    print(f'train_start_date: {args.train_start_date}')
    print(f'notebook_steps: {args.steps}')
    print(f'data_split_path: {args.data_split_path}')
    print(f'feature_count: {args.feature_count}')
    print(f'scale_pos_multiply_factor: {args.scale_pos_multiply_factor}')
    print(f'eval_metric: {args.eval_metric}')
    print(f'run_type: {args.run_type}')
    
    
    
    
    valid_run_types = ['all', 'multiclass','binary']
    
    if args.run_type not in valid_run_types:
        raise Exception(args.run_type +'is not valid run_type. steps must be one of ' + ','.join(valid_run_types))
    
    
    
    steps = list(args.steps.split(','))
    valid_steps = ['train','evaluate']
    for check_each_step in steps:
        if check_each_step not in valid_steps:
            raise Exception(check_each_step +'is not valid step. steps must be one of ' + ','.join(valid_steps))
    
    generic_utils.run_scheduler(chief_address, chief_port)
    
    gcs_full_base_path = args.base_gcs_path + '/' + run_name
    
    bucket_name, output_path = generic_utils.parse_gcs_path(gcs_full_base_path)
    for each_step in steps:
        if each_step == 'train':
            notebook_parameters['max_depth_env'] = args.max_depth
            notebook_parameters['min_child_weight_env'] = args.min_child_weight
            notebook_parameters['learning_rate_env'] = args.learning_rate
            notebook_parameters['num_booster_env'] = args.num_booster
            notebook_parameters['feature_count_env'] = args.feature_count
            notebook_parameters['scale_pos_multiply_factor'] = args.scale_pos_multiply_factor
            notebook_parameters['eval_metric_env'] =  args.eval_metric

            generic_utils.execute_notebook('train_notebook.ipynb', notebook_parameters, args.kernel_name, bucket_name, output_path + '/train_notebook', 'train_output')
            
        elif each_step == 'evaluate':
            generic_utils.execute_notebook('eval_notebook.ipynb', notebook_parameters, args.kernel_name, bucket_name, output_path + '/eval_notebook', 'eval_output')
            #generic_utils.execute_notebook('metric_notebook.ipynb', notebook_parameters, args.kernel_name, bucket_name, output_path + '/metric_notebook', 'metric_output')
            
        
    
    
def main_worker(chief_address, args=None):
    print("args", args)
    parser = argparse.ArgumentParser(description='Running Dask')
    
    parser.add_argument(
        '--kernel_name',
        dest='kernel_name',
        type=str,
        required=True,
        help='kernel_name')
    
    parser.add_argument(
        '--num_workers',
        dest='num_workers',
        type=int,
        required=False,
        help='num_workers')
    
    parser.add_argument(
        '--no_worker_threads',
        dest='no_worker_threads',
        type=int,
        required=False,
        help='no_worker_threads')
    
    parser.add_argument(
        '--memory_limit',
        dest='memory_limit',
        type=str,
        required=False,
        help='memory_limit')
    
    
    
    args = parser.parse_args(args)
    
    print(f'memory_limit: {args.memory_limit}')
    print(f'no_worker_threads: {args.no_worker_threads}')
    print(f'num_workers: {args.num_workers}')
    
    generic_utils.run_worker(chief_address, args.num_workers, args.num_workers, args.memory_limit)
    
    
if __name__ == '__main__':
    workerpool_type, chief_ip, chief_port, chief_address, workerpool1_nodes_len = generic_utils.get_cluster_config()
    #workerpool_type = 'workerpool0'
    #chief_ip = '127.0.0.1'
    #chief_port = 8787
    #chief_address = None
    
    if workerpool_type == "workerpool0":    
        main_scheduler(chief_address, chief_port, workerpool1_nodes_len)
    else:
        main_worker(chief_address)