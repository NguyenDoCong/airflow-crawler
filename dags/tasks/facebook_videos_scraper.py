from airflow.decorators import task
from utils.account_videos import AccountVideo
# from utils.downloader import batch_download_from_file

import sys
sys.path.append('/opt/airflow/dags')

# @task
def facebook_videos_scraper(id = "official.parkhangseo", FACEBOOK_FILE_PATH="", DOWNLOAD_DIRECTORY="media", scrolls=5):
    
    videos_scraper = AccountVideo(id)
    return videos_scraper.save_video_urls_to_database_pipeline(scrolls=scrolls, user_id=id)
    # batch_download_from_file(FACEBOOK_FILE_PATH, DOWNLOAD_DIRECTORY, tiktok=False)