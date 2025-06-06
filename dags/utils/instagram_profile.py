from dags.app.worker.schema import TaskStatus
from dags.utils.downloader import download_video
from .instagram_base import BaseInstagramScraper
# from config import Config as config
# from ..logs import Logs
from .scroll import scroll_page_callback
from selenium.webdriver.common.by import By
from rich import print as rprint
from .output import print_no_data_info
from selenium.webdriver.support import expected_conditions as EC
from config import Config

# logs = Logs()

from app.core.database_utils import get_info_by_user_id
from dags.utils.get_id import extract_id

class ProfileScraper(BaseInstagramScraper):

    def __init__(self, user_id: str) -> None:
        super().__init__(user_id, base_url=f"https://www.instagram.com/{user_id}/reels/")
        self.success = False
        self._driver.add_cookie(
            {
                "name": "sessionid",
                "value": Config.INSTAGRAM_SESSIONID_VALUE,
                "domain": ".instagram.com",
            }
        )
        self._refresh_driver()

    def _refresh_driver(self) -> None:
        """Load cookies and refresh driver"""
        self._driver.refresh()
    
    def extract_videos(self, downloads=10):
        extracted_video_urls = []
        print("Extracting videos...")
        try:
            def extract_callback(driver):

                video_elements = self._driver.find_elements(By.TAG_NAME, "a")
                print(f"Found {len(video_elements)} video tags")
                for video_element in video_elements:
                    src_attribute = video_element.get_attribute("href")
                    if src_attribute and src_attribute not in extracted_video_urls and "/reel/" in src_attribute:
                        rprint(f"Extracted video URL: {src_attribute}")
                        extracted_video_urls.append(src_attribute)
            scrolls =1
            while len(extracted_video_urls) < downloads:
                scroll_page_callback(self._driver, extract_callback, scrolls=scrolls)
                scrolls += 1

        except Exception as e:
            # logs.log_error(f"An error occurred while extracting videos: {e}")
            print(f"An error occurred while extracting videos: {e}")
            pass

        print(f"Extracted {len(extracted_video_urls)} video URLs")
        return extracted_video_urls

  

    def pipeline_videos(self, id, downloads=10):
        """
        Pipeline to scrape videos
        
        Returns:
            list: List of downloaded video results
            list: Empty list if no new videos or error occurs
        """
        # results = []
        try:
            rprint(f"[bold]Step 1 of 2 - Loading profile page[/bold]")
            video_urls = self.extract_videos(downloads=downloads)

            if not video_urls:
                print_no_data_info()
                self.success = False
                return {'id': id, 'new_links': []}
                
            rprint(f"[bold]Step 2 of 2 - Downloading and saving videos [/bold]")
            rprint("[bold red]Don't close the app![/bold red] Saving scraped data to database, it can take a while!")

            # Filter existing videos
            db_videos = get_info_by_user_id(platform="instagram", user_id=id)
            for video in db_videos:
                if video.url in video_urls:
                    video_urls.remove(video.url)
            
            video_urls = video_urls[:downloads]  # Limit the number of new videos
            
            new_links = set(video_urls)
            print(f"New videos: {len(new_links)}")

            if not new_links:
                self.success = True
                return {'id': id, 'new_links': []}

            self.success = True

        except Exception as e:
            rprint(f"An error occurred: {str(e)}")
            self.success = False
        
        finally:
            if hasattr(self, '_driver'):
                try:
                    self._driver.quit()
                except:
                    pass

        return {'id': id, 'new_links': new_links}
