# # dags/pipeline_request_dag.py

# from airflow import DAG
# from airflow.utils.dates import days_ago
# from tasks.conf_example import print_env

# with DAG(
#     dag_id="pipeline_request",
#     schedule_interval=None,
#     start_date=days_ago(1),
#     catchup=False,
#     tags=["example"],
# ) as dag:

#     print_env_task = print_env('dag_run')
