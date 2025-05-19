from airflow import DAG
from airflow.utils.dates import days_ago
from dags.tasks.instagram_scraper import instagram_videos_scraper
from tasks.get_transcript import audio_to_transcript
from config import Config
from airflow.operators.python import PythonOperator

# Define the DAG
       
def run_instagram_videos_scraper(**context):
    conf = context["dag_run"].conf or {}
    id = conf.get("id", "hoaminzy_hoadambut")
    scrolls = conf.get("count", 10)
    return instagram_videos_scraper(
        id=id,
        scrolls=scrolls,
    )

with DAG(
    dag_id="instagram_videos_scraper_dag",
    schedule_interval=None,  # Set your desired schedule
    start_date=days_ago(1),
    catchup=False,
) as dag:

    downloads = PythonOperator(
        task_id="instagram_videos_scraper_task",
        provide_context=True,
        python_callable=run_instagram_videos_scraper,
    )

    transcript = PythonOperator(
        task_id="audio_to_transcript_task",
        python_callable=audio_to_transcript,
        provide_context=True,
        op_kwargs={"platform": "instagram"},
    )

    downloads >> transcript


