from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.tiktok_videos_scraper import tiktok_videos_scraper
from tasks.get_transcript import audio_to_transcript
from config import Config
from airflow.operators.python import PythonOperator

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

with DAG(
    dag_id="tiktok_videos_scraper_dag",
    schedule_interval=None,  # Set your desired schedule
    start_date=days_ago(1),
    catchup=False,
) as dag:

    downloads = PythonOperator(
        task_id="tiktok_videos_scraper_task",
        # python_callable=tiktok_videos_scraper,
        # op_args=["hoaminzy_hoadambut", 10, Config.MS_TOKENS, Config.DOWNLOAD_DIRECTORY],
        provide_context=True,
        python_callable=run_tiktok_videos_scraper,
    )

    # transcript = audio_to_transcript(downloads, platform="tiktok")
    transcript = PythonOperator(
        task_id="audio_to_transcript_task",
        python_callable=audio_to_transcript,
        # op_args=[downloads.output],
        provide_context=True,
        op_kwargs={"platform": "tiktok"},
    )

    downloads >> transcript