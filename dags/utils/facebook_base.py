import pickle
import json
import tempfile

from rich import print as rprint
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from .scraper import Scraper

from config import Config
import os
# from ...logs import Logs

# logs = Logs()


class BaseFacebookScraper(Scraper):
    def __init__(self, user_id: str, base_url: str) -> None:
        super().__init__()
        self._user_id = user_id
        self._base_url = base_url.format(self._user_id)
        options = self._chrome_driver_configuration()
        
        user_data_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--headless=new")

        self._driver = webdriver.Chrome(options=options)
        self._driver.get(self._base_url)
        self._wait = WebDriverWait(self._driver, 10)
        self.success = False

    def _load_cookies(self) -> None:
        try:
            self._driver.delete_all_cookies()
            if not os.path.exists("dags/utils/fb_cookies.json"):
                print("No cookies file found. Please login to Facebook and save cookies.")
            else:
                with open("dags/utils/fb_cookies.json", "rb") as file:
                    cookies = pickle.load(file)
                    for cookie in cookies:
                        try:
                            self._driver.add_cookie(cookie)
                        except Exception as e:
                            # logs.log_error(f"An Error occurred adding cookies {e}")
                            rprint(f"An Error occurred while adding cookies {e}")

        except Exception as e:
            # logs.log_error(f"An Error occurred while loading cookies: {e}")
            rprint(f"An Error occurred while loading cookies {e}")

   