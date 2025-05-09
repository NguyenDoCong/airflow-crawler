from selenium.webdriver.chrome.options import Options
import tempfile

class Scraper:
    """
    Base class for web scrapers.

    This class provides common methods and configurations for web scraping tasks using Selenium.

    Attributes:
        None

    Methods:
        _chrome_driver_configuration() -> Options:
            Configures Chrome WebDriver options for Selenium.

            Returns:
                Options: A configured ChromeOptions instance to be used with Chrome WebDriver.
    """

    @staticmethod
    def _chrome_driver_configuration() -> Options:
        """
        Configures Chrome WebDriver options for Selenium.

        This static method creates a set of options that can be passed to the Chrome WebDriver
        when creating an instance of it. These options modify the behavior of the Chrome browser
        during automated testing or scraping.

        Returns:
            Options: A configured ChromeOptions instance to be used with Chrome WebDriver.
        """
        chrome_options = Options()
        user_data_dir = tempfile.mkdtemp()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument(
            "--disable-features=IsolateOrigins,site-per-process"
        )
        chrome_options.add_argument(
            "--enable-features=NetworkService,NetworkServiceInProcess"
        )
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return chrome_options
