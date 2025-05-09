from airflow.decorators import task
from utils.account_videos import AccountVideo
from utils.downloader import batch_download_from_file

import sys
sys.path.append('/opt/airflow/dags')

@task
def fb_videos_scraper(id = "official.parkhangseo", FACEBOOK_FILE_PATH="", DOWNLOAD_DIRECTORY="media", scrolls=5):
    
    videos_scraper = AccountVideo(id)
    videos_scraper.save_video_urls_to_database_pipeline(scrolls=scrolls)
    # batch_download_from_file(FACEBOOK_FILE_PATH, DOWNLOAD_DIRECTORY, tiktok=False)