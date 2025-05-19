from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.facebook_videos_scraper import facebook_videos_scraper
from tasks.get_transcript import audio_to_transcript
from tasks.x_login import x_login
from config import Config
from airflow.operators.python import PythonOperator

# Define the DAG
       
def run_facebook_videos_scraper(**context):
    conf = context["dag_run"].conf or {}
    id = conf.get("id", "hoaminzy_hoadambut")
    scrolls = conf.get("count", 10)
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

    downloads = PythonOperator(
        task_id="facebook_videos_scraper_task",
        provide_context=True,
        python_callable=run_facebook_videos_scraper,
    )

    transcript = PythonOperator(
        task_id="audio_to_transcript_task",
        python_callable=audio_to_transcript,
        provide_context=True,
        op_kwargs={"platform": "facebook"},
    )

    downloads >> transcript