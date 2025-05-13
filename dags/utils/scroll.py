from time import sleep

from config import Config
# from ..logs import Logs

# logs = Logs()
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scroll_page(driver, scrolls=10) -> None:
    """
    Scrolls the page to load more data from a website
    """
    try:
        print(f"Scrolling {scrolls} iterations...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        # print(f"Last height: {last_height}")
        consecutive_scrolls = 0
        count = 0

        while consecutive_scrolls < Config.MAX_CONSECUTIVE_SCROLLS:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            sleep(Config.SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                consecutive_scrolls += 1
            else:
                consecutive_scrolls = 0

            last_height = new_height
            count += 1
            if count >scrolls:
                # logs.log_info("Scrolling stopped after 10 iterations")
                print(f"Scrolling stopped after {count} iterations")
                break
            # logs.log_info(f"Scrolling... {count} iterations")

        print(f"Scrolled {count} iterations")

    except Exception as e:
        # logs.log_error(f"Error occurred while scrolling: {e}")
        print(f"Error occurred while scrolling: {e}")


def scroll_page_callback(driver, callback, scrolls =10) -> None:
    """
    Scrolls the page to load more data from a website
    """
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        consecutive_scrolls = 0
        count = 0
        # reels_tab = driver.find_element(
        #             By.XPATH, "//a[contains(@href, '/reels/')]"
        #         )
        # reels_tab.click()
        # # Wait for the page to load
        # WebDriverWait(driver, Config.WAIT_TIME).until(
        #     EC.presence_of_all_elements_located(
        #         (By.TAG_NAME, "a")
        #     )
        # )

        while consecutive_scrolls < Config.MAX_CONSECUTIVE_SCROLLS:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            sleep(Config.SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                consecutive_scrolls += 1
            else:
                consecutive_scrolls = 0

            last_height = new_height

            count += 1
            print(f"Count: {count}, Limit: {scrolls}")
            if count >scrolls:
                print("Scrolling stopped after 10 iterations")
                break

            callback(driver)

            print(f"Scrolled {count} iterations")
            

    except Exception as e:
        # logs.log_error(f"Error occurred while scrolling: {e}")
        print(f"Error occurred while scrolling: {e}")

