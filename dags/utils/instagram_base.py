from .scraper import Scraper
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
# from config import Config as config
# from ..logs import Logs

# logs = Logs()


class BaseInstagramScraper(Scraper):
    def __init__(self, user_id: str, base_url: str) -> None:
        super().__init__()
        self._user_id = user_id
        self._base_url = base_url.format(self._user_id)
        options = self._chrome_driver_configuration()
        # options = Options()
        user_data_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={user_data_dir}")

        options.add_argument("--headless=new")

        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        self._driver = webdriver.Chrome(options=options)
        print(f"url: {self._base_url}")
        self._driver.get(self._base_url)
        self._wait = WebDriverWait(self._driver, 10)
        self.success = False
