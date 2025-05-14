from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.tiktok_videos_scraper import tiktok_videos_scraper
from tasks.get_transcript import audio_to_transcript
from config import Config

import sys
sys.path.append('/opt/airflow/dags')
# Define the DAG

with DAG(
    dag_id="tiktok_videos_scraper_dag",
    schedule_interval=None,  # Set your desired schedule
    start_date=days_ago(1),
    catchup=False,
) as dag:
    downloads= tiktok_videos_scraper(id="hoaminzy_hoadambut", 
                                        count=50, 
                                        ms_tokens=Config.MS_TOKENS, 
                                        # TIKTOK_ERROR_FILE_PATH=Config.TIKTOK_ERROR_FILE_PATH, 
                                        # TIKTOK_FILE_PATH=Config.TIKTOK_FILE_PATH,
                                        DOWNLOAD_DIRECTORY=Config.DOWNLOAD_DIRECTORY)

    transcript = audio_to_transcript(downloads, platform="tiktok")
 