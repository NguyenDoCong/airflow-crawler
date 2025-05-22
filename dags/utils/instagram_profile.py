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

from app.core.database_utils import create_pending_video, get_all_videos_from_db, update_video_status
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
    
    def extract_videos(self, scrolls=10):
        extracted_video_urls = []
        print("Extracting videos...")
        try:
            def extract_callback(driver):
                # Click to reels tab
                # reels_tab = self._driver.find_element(
                #     By.XPATH, "//a[contains(@href, '/reels/')]"
                # )
                # reels_tab.click()
                # # Wait for the page to load
                # self._wait.until(
                #     EC.presence_of_all_elements_located(
                #         (By.TAG_NAME, "a")
                #     )
                # )
                # Find all video elements
                video_elements = self._driver.find_elements(By.TAG_NAME, "a")
                print(f"Found {len(video_elements)} video tags")
                for video_element in video_elements:
                    src_attribute = video_element.get_attribute("href")
                    if src_attribute and src_attribute not in extracted_video_urls and "/reel/" in src_attribute:
                        rprint(f"Extracted video URL: {src_attribute}")
                        extracted_video_urls.append(src_attribute)

            scroll_page_callback(self._driver, extract_callback, scrolls=scrolls)

        except Exception as e:
            # logs.log_error(f"An error occurred while extracting videos: {e}")
            print(f"An error occurred while extracting videos: {e}")
            pass

        print(f"Extracted {len(extracted_video_urls)} video URLs")
        return extracted_video_urls

  

    def pipeline_videos(self, id, scrolls=10):
        """
        Pipeline to scrape videos
        
        Returns:
            list: List of downloaded video results
            list: Empty list if no new videos or error occurs
        """
        # results = []
        try:
            rprint(f"[bold]Step 1 of 2 - Loading profile page[/bold]")
            video_urls = self.extract_videos(scrolls=scrolls)

            if not video_urls:
                print_no_data_info()
                self.success = False
                return {'id': id, 'new_links': []}
                
            rprint(f"[bold]Step 2 of 2 - Downloading and saving videos [/bold]")
            rprint("[bold red]Don't close the app![/bold red] Saving scraped data to database, it can take a while!")

            # Filter existing videos
            db_videos = get_all_videos_from_db(platform="instagram")
            for video in db_videos:
                if video.url in video_urls:
                    video_urls.remove(video.url)
            
            new_links = set(video_urls)
            print(f"New videos: {len(new_links)}")

            if not new_links:
                self.success = True
                return {'id': id, 'new_links': []}

            # for link in new_links:
            #     try:
            #         video_id = extract_id(link)
            #         task_id = create_pending_video(video_id, id, link, platform='instagram')
            #         file_path = download_video(link, Config.DOWNLOAD_DIRECTORY)
                    
            #         if file_path:
            #             update_video_status(video_id, TaskStatus.PROCESSING.value, platform="instagram")
            #             result = {
            #                 "video_id": video_id,
            #                 "file_path": file_path,
            #             }
            #             print(f"Downloaded video {result['video_id']} to {result['file_path']}")
            #             results.append(result)
            #         else:
            #             update_video_status(video_id, TaskStatus.FAILURE.value, platform="instagram", logs="Error downloading video")
            #     except Exception as e:
            #         rprint(f"Error downloading video {link}: {str(e)}")
            #         continue

            # print(f"Downloaded {len(results)} new videos.")
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
