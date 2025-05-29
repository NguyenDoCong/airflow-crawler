from airflow import DAG
from airflow.utils.dates import days_ago
from dags.tasks.instagram_scraper import instagram_videos_scraper
from tasks.get_transcript import audio_to_transcript
from tasks.batch_download import batch_download
from config import Config
from airflow.operators.python import PythonOperator
import math
from datetime import datetime, timedelta
import logging

# Define the DAG
       
def run_instagram_videos_scraper(**context):
    conf = context["dag_run"].conf or {}
    id = conf.get("id", "cristiano")
    downloads = conf.get("count", 20)
    return instagram_videos_scraper(
        id=id,
        downloads=downloads,
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
        "retry_delay": timedelta(minutes=1),
        'on_success_callback': lambda context: logging.info("DAG runs successfully"),
        'on_retry_callback': log_retry,
        'on_failure_callback': lambda context: logging.error("DAG failed"),
    },
    dag_id="instagram_videos_scraper_dag",
    schedule="@daily",
    start_date=days_ago(0),
    catchup=False,
) as dag:

    urls = PythonOperator(
        task_id="get_links_task",
        provide_context=True,
        python_callable=run_instagram_videos_scraper,
        execution_timeout=timedelta(seconds=90)                  
    )

    downloads = PythonOperator(
        task_id="batch_download_task",
        python_callable=batch_download,
        provide_context=True,
        op_kwargs={"platform": "instagram"},
    )

    transcript = PythonOperator(
        task_id="audio_to_transcript_task",
        python_callable=audio_to_transcript,
        provide_context=True,
        op_kwargs={"platform": "instagram"},
    )

    urls >> downloads >> transcript


