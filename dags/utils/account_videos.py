from typing import List

from rich import print as rprint
from selenium.webdriver.common.by import By

from dags.app.worker.schema import TaskStatus
from dags.utils.downloader import download_video
from .facebook_base import BaseFacebookScraper
from .scroll import scroll_page
# from ...logs import Logs
from utils import output
from config import Config

from app.core.database_utils import create_pending_video, get_all_videos_from_db, update_video_status
from dags.utils.get_id import extract_id

# logs = Logs()

class AccountVideo(BaseFacebookScraper):
    """
    Scrape user's pictures
    """

    def __init__(self, user_id: str) -> None:
        super().__init__(user_id, base_url=f"https://www.facebook.com/{user_id}/videos")
        self.success = False

    def _load_cookies_and_refresh_driver(self) -> None:
        """Load cookies and refresh driver"""
        self._load_cookies()
        self._driver.refresh()

    @property
    def is_pipeline_successful(self) -> bool:
        return self.success

    @staticmethod
    def extract_urls(video_elements) -> List[str]:
        extracted_videos_urls = []
        for video_element in video_elements:
            src_attribute = video_element.get_attribute("href")
            if src_attribute:
                extracted_videos_urls.append(src_attribute)
        return extracted_videos_urls

    def scrape_video_urls(self) -> List[str]:
        """
        Return a list of all the video urls
        """

        a_tag_elements = self._driver.find_elements(By.TAG_NAME, "a")    
        print(f"Found {len(a_tag_elements)} a tags")
        href_elements = []
        for a_tag in a_tag_elements:
            href = a_tag.get_attribute("href")
            if href and "/videos/" in href and href not in href_elements:
                href_elements.append(href)
                print(f"Found href: {href}")
        print(f"Found {len(href_elements)} href elements")

        return href_elements

    def save_video_urls_to_database_pipeline(self, scrolls=10) -> None:
        """Pipeline to save video url to database"""
        try:
            rprint("[bold]Step 1 of 3 - Load cookies[/bold]")
            self._load_cookies_and_refresh_driver()

            rprint("[bold]Step 2 of 3 - Scrolling page[/bold]")
            scroll_page(self._driver, scrolls=scrolls)

            rprint("[bold]Step 3 of 3 - Extract videos urls[/bold]")
            videos = self.scrape_video_urls()

            if not videos:
                output.print_no_data_info()
                self._driver.quit()
                self.success = False
            else:
                output.print_list(videos)

                rprint(
                    "[bold red]Don't close the app![/bold red] Saving scraped data to database, it can take a while!"
                )
                
                results = get_all_videos_from_db()
                for result in results:
                    if result.url in videos:
                        videos.remove(result.url)
                print(f"Remaining new videos: {len(videos)}")

                new_links = set(videos)

                print(f"New videos: {len(new_links)}")

                for link in new_links:
                    video_id = extract_id(link)
                    task_id = create_pending_video(video_id, link)
                    result = download_video(link, Config.DOWNLOAD_DIRECTORY)
                    if result:
                        update_video_status(video_id, TaskStatus.PROCESSING.value, platform="facebook")
                    else:
                        update_video_status(video_id, TaskStatus.FAILURE.value, platform="facebook")

                # with open(Config.downloaded_videos_file, "a") as f:
                #     for link in new_links:
                #         f.write(link + "\n")   

                self._driver.quit()
                self.success = True

        except Exception as e:
            # logs.log_error(f"An error occurred: {e}")
            rprint(f"An error occurred {e}")

