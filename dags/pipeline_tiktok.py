from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.tiktok_videos_scraper import tiktok_videos_scraper
from tasks.batch_download import batch_download
from tasks.get_transcript import audio_to_transcript
from config import Config
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging

import sys
sys.path.append('/opt/airflow/dags')
# Define the DAG

def run_tiktok_videos_scraper(**context):
    conf = context["dag_run"].conf or {}
    id = conf.get("id", "hoaminzy_hoadambut")
    count = conf.get("count", 10)
    ms_tokens = conf.get("ms_tokens", Config.MS_TOKENS)
    download_directory = conf.get("download_directory", Config.DOWNLOAD_DIRECTORY)
    return tiktok_videos_scraper(
        id=id,
        count=count,
        ms_tokens=ms_tokens,
        DOWNLOAD_DIRECTORY=download_directory
    )

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
    dag_id="tiktok_videos_scraper_dag",
    schedule="@daily",
    start_date=days_ago(0),
    catchup=False,
) as dag:

    urls = PythonOperator(
        task_id="get_links_task",
        provide_context=True,
        python_callable=run_tiktok_videos_scraper,
        execution_timeout=timedelta(seconds=90)          
    )

    downloads = PythonOperator(
        task_id="batch_download_task",
        python_callable=batch_download,
        provide_context=True,
        op_kwargs={"platform": "tiktok"},
    )

    transcript = PythonOperator(
        task_id="audio_to_transcript_task",
        python_callable=audio_to_transcript,
        provide_context=True,
        op_kwargs={"platform": "tiktok"},
    )

    urls >> downloads >> transcript