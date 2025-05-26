from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.get_transcript import audio_to_transcript
from tasks.x_videos_scraper import x_videos_scraper
from tasks.x_login import x_login
from tasks.batch_download import batch_download
from config import Config
from airflow.operators.python import PythonOperator
import math
from datetime import datetime, timedelta
import logging

import sys
sys.path.append('/opt/airflow/dags')
# Define the DAG

def run_x_videos_scraper(**context):
    conf = context["dag_run"].conf or {}
    id = conf.get("id", "Cristiano")
    downloads = conf.get("count", 20)
    return x_videos_scraper(
        id=id,
        downloads=downloads,
    )

def login_x(**context):
    conf = context["dag_run"].conf or {}
    X_USERNAME = conf.get("X_USERNAME", Config.X_USERNAME)
    X_PASSWORD = conf.get("X_PASSWORD", Config.X_PASSWORD)
    return x_login(X_PASSWORD=X_PASSWORD,
                            X_USERNAME=X_USERNAME)
def log_retry(context):
    try_number = context['ti'].try_number
    max_tries = context['ti'].max_tries
    task_id = context['ti'].task_id
    logging.info(f"Retrying task {task_id}: attempt {try_number} of {max_tries + 1}")

with DAG(
    default_args={
        "depends_on_past": False,
        "retries": 5,
        "retry_delay": timedelta(minutes=5),
        # 'execution_timeout': timedelta(seconds=90),
        'on_success_callback': lambda context: logging.info("DAG runs successfully"),
        'on_retry_callback': log_retry,
        'on_failure_callback': lambda context: logging.error("DAG failed"),        
    },
    dag_id="x_videos_scraper_dag",
    schedule="@daily",
    start_date=days_ago(0),
    catchup=False,
) as dag:
    
    login = PythonOperator(
        task_id="x_login_task",
        provide_context=True,
        python_callable=login_x,
    )

    urls = PythonOperator(
        task_id="get_links_task",
        provide_context=True,
        python_callable=run_x_videos_scraper,
        execution_timeout=timedelta(seconds=90)          
    )

    downloads = PythonOperator(
        task_id="batch_download_task",
        python_callable=batch_download,
        provide_context=True,
        op_kwargs={"platform": "x"},
    )

    transcript = PythonOperator(
        task_id="audio_to_transcript_task",
        python_callable=audio_to_transcript,
        provide_context=True,
        op_kwargs={"platform": "x"},
    )

    login >> urls >> downloads >> transcript
