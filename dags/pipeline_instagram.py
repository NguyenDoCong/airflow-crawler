from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.insta_scraper import ins_videos_scraper
from tasks.get_transcript import audio_to_transcript
from config import Config

# Define the DAG
       
with DAG(
    dag_id="instagram_videos_scraper_dag",
    schedule_interval=None,  # Set your desired schedule
    start_date=days_ago(1),
    catchup=False,
) as dag:
    downloads = ins_videos_scraper(id="baukrysie",
                                    INSTAGRAM_FILE_PATH=Config.INSTAGRAM_FILE_PATH,
                                    download_directory=Config.DOWNLOAD_DIRECTORY,
                                    scrolls=15)
    transcript = audio_to_transcript(downloads, platform="instagram")


