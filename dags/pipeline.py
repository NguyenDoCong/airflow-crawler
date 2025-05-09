from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.tiktok_videos_scraper import tiktok_videos_scraper
from tasks.x_videos_scraper import x_videos_scraper
from tasks.insta_scraper import ins_videos_scraper
from tasks.fb_videos_scraper import fb_videos_scraper
from tasks.x_login import x_login
from config import Config

# Define the DAG

# with DAG(
#     dag_id="tiktok_videos_scraper_dag",
#     schedule_interval=None,  # Set your desired schedule
#     start_date=days_ago(1),
#     catchup=False,
# ) as dag:
#     scrape_task = tiktok_videos_scraper(id="therock", 
#                                         count=10, 
#                                         ms_tokens=Config.MS_TOKENS, 
#                                         TIKTOK_ERROR_FILE_PATH=Config.TIKTOK_ERROR_FILE_PATH, 
#                                         TIKTOK_FILE_PATH=Config.TIKTOK_FILE_PATH,
#                                         DOWNLOAD_DIRECTORY=Config.DOWNLOAD_DIRECTORY)
    
# with DAG(
#     dag_id="x_login_dag",
#     schedule_interval=None,  # Set your desired schedule
#     start_date=days_ago(1),
#     catchup=False,
# ) as dag:
#     scrape_task = x_login(X_USERNAME=Config.X_USERNAME,
#                           X_PASSWORD=Config.X_PASSWORD)
    
with DAG(
    dag_id="x_videos_scraper_dag",
    schedule_interval=None,  # Set your desired schedule
    start_date=days_ago(1),
    catchup=False,
) as dag:
    scrape_task = x_videos_scraper(id="elonmusk",
                                    scrolls=5)
         
# with DAG(
#     dag_id="instagram_videos_scraper_dag",
#     schedule_interval=None,  # Set your desired schedule
#     start_date=days_ago(1),
#     catchup=False,
# ) as dag:
#     scrape_task = ins_videos_scraper(id="baukrysie",
#                                     INSTAGRAM_FILE_PATH=Config.INSTAGRAM_FILE_PATH,
#                                     download_directory=Config.DOWNLOAD_DIRECTORY,
#                                     scrolls=10)

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