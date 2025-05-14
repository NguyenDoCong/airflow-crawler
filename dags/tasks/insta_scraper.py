from airflow.decorators import task
from utils.instagram_profile import ProfileScraper 
# from utils.downloader import batch_download_from_file

import sys
sys.path.append('/opt/airflow/dags')

@task
def ins_videos_scraper(id = "baukrysie",INSTAGRAM_FILE_PATH="", download_directory="media", scrolls=10):
    """
    Scrape videos from an Instagram profile and download them.  
    Args:
        id (str): Instagram profile ID.
        INSTAGRAM_FILE_PATH (str): Path to save the scraped video URLs.
        download_directory (str): Directory to save the downloaded videos.
    """
    scraper = ProfileScraper(id)
    return scraper.pipeline_videos(scrolls=scrolls)
    # batch_download_from_file(INSTAGRAM_FILE_PATH, download_directory, tiktok=False)
