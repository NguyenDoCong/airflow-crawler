from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.get_transcript import audio_to_transcript
from tasks.x_videos_scraper import x_videos_scraper
from tasks.x_login import x_login
from config import Config

import sys
sys.path.append('/opt/airflow/dags')
# Define the DAG

with DAG(
    dag_id="x_login_dag",
    schedule_interval=None,  # Set your desired schedule
    start_date=days_ago(1),
    catchup=False,
) as dag:
    x_login_task = x_login(X_PASSWORD=Config.X_PASSWORD,
                            X_USERNAME=Config.X_USERNAME)

with DAG(
    dag_id="x_videos_scraper_dag",
    schedule_interval=None,  # Set your desired schedule
    start_date=days_ago(1),
    catchup=False,
) as dag:
    downloads = x_videos_scraper(id="elonmusk",
                                    scrolls=10)
    transcript = audio_to_transcript(downloads, platform="x")
