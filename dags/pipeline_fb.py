from airflow import DAG
from airflow.utils.dates import days_ago
from dags.tasks.facebook_videos_scraper import facebook_videos_scraper
from tasks.get_transcript import audio_to_transcript
from tasks.batch_download import batch_download
from config import Config
from airflow.operators.python import PythonOperator
import math

# Define the DAG
       
def run_facebook_videos_scraper(**context):
    conf = context["dag_run"].conf or {}
    id = conf.get("id", "hoaminzy_hoadambut")
    scrolls = math.ceil(conf.get("count", 20)/20)
    return facebook_videos_scraper(
        id=id,
        scrolls=scrolls,
    )

with DAG(
    dag_id="facebook_videos_scraper_dag",
    schedule_interval=None,  # Set your desired schedule
    start_date=days_ago(1),
    catchup=False,
) as dag:

    urls = PythonOperator(
        task_id="get_links_task",
        provide_context=True,
        python_callable=run_facebook_videos_scraper,
    )

    downloads = PythonOperator(
        task_id="batch_download_task",
        python_callable=batch_download,
        provide_context=True,
        op_kwargs={"platform": "facebook"},
    )

    transcript = PythonOperator(
        task_id="audio_to_transcript_task",
        python_callable=audio_to_transcript,
        provide_context=True,
        op_kwargs={"platform": "facebook"},
    )

    urls >> downloads >> transcript