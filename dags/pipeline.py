from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.tiktok_videos_scraper import tiktok_videos_scraper
from tasks.x_videos_scraper import x_videos_scraper
from tasks.insta_scraper import ins_videos_scraper
from tasks.fb_videos_scraper import fb_videos_scraper
from tasks.get_transcript import audio_to_transcript
from app.core.database_utils import update_video_status
from app.worker.schema import TaskStatus
from tasks.x_login import x_login
from config import Config

# Define the DAG

# with DAG(
#     dag_id="tiktok_videos_scraper_dag",
#     schedule_interval=None,  # Set your desired schedule
#     start_date=days_ago(1),
#     catchup=False,
# ) as dag:
#     downloads= tiktok_videos_scraper(id="hoaminzy_hoadambut", 
#                                         count=1, 
#                                         ms_tokens=Config.MS_TOKENS, 
#                                         TIKTOK_ERROR_FILE_PATH=Config.TIKTOK_ERROR_FILE_PATH, 
#                                         TIKTOK_FILE_PATH=Config.TIKTOK_FILE_PATH,
#                                         DOWNLOAD_DIRECTORY=Config.DOWNLOAD_DIRECTORY)

#     transcript = audio_to_transcript(downloads, platform="tiktok")
 
    
# with DAG(
#     dag_id="x_login_dag",
#     schedule_interval=None,  # Set your desired schedule
#     start_date=days_ago(1),
#     catchup=False,
# ) as dag:
#     scrape_task = x_login(X_USERNAME=Config.X_USERNAME,
#                           X_PASSWORD=Config.X_PASSWORD)
    
# with DAG(
#     dag_id="x_videos_scraper_dag",
#     schedule_interval=None,  # Set your desired schedule
#     start_date=days_ago(1),
#     catchup=False,
# ) as dag:
#     downloads = x_videos_scraper(id="elonmusk",
#                                     scrolls=5)
#     transcript = audio_to_transcript(downloads, platform="x")

         
with DAG(
    dag_id="instagram_videos_scraper_dag",
    schedule_interval=None,  # Set your desired schedule
    start_date=days_ago(1),
    catchup=False,
) as dag:
    downloads = ins_videos_scraper(id="baukrysie",
                                    INSTAGRAM_FILE_PATH=Config.INSTAGRAM_FILE_PATH,
                                    download_directory=Config.DOWNLOAD_DIRECTORY,
                                    scrolls=10)
    transcript = audio_to_transcript(downloads, platform="instagram")

# with DAG(
#     dag_id="facebook_videos_scraper_dag",
#     schedule_interval=None,  # Set your desired schedule
#     start_date=days_ago(1),
#     catchup=False,
# ) as dag:
#     scrape_task = fb_videos_scraper(id="official.parkhangseo",
#                                     FACEBOOK_FILE_PATH=Config.FACEBOOK_FILE_PATH,
#                                     DOWNLOAD_DIRECTORY=Config.DOWNLOAD_DIRECTORY,
#                                     scrolls=5)
    
