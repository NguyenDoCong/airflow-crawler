from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.fb_videos_scraper import fb_videos_scraper
from tasks.get_transcript import audio_to_transcript
from tasks.x_login import x_login
from config import Config

# Define the DAG

with DAG(
    dag_id="facebook_videos_scraper_dag",
    schedule_interval=None,  # Set your desired schedule
    start_date=days_ago(1),
    catchup=False,
) as dag:
    downloads = fb_videos_scraper(id="official.parkhangseo",
                                    FACEBOOK_FILE_PATH=Config.FACEBOOK_FILE_PATH,
                                    DOWNLOAD_DIRECTORY=Config.DOWNLOAD_DIRECTORY,
                                    scrolls=10)
    transcript = audio_to_transcript(downloads, platform="facebook")
