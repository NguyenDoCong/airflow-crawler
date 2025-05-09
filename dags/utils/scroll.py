from time import sleep

from config import Config
# from ..logs import Logs

# logs = Logs()


def scroll_page(driver, scrolls =10) -> None:
    """
    Scrolls the page to load more data from a website
    """
    try:
        print("Scrolling...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        # print(f"Last height: {last_height}")
        consecutive_scrolls = 0
        # count = 0

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
                print("Scrolling stopped after 10 iterations")
                break
            print(f"Scrolling... {count} iterations")
    except Exception as e:
        print(f"Error occurred while scrolling: {e}")


def scroll_page_callback(driver, callback, scrolls =10) -> None:
    """
    Scrolls the page to load more data from a website
    """
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
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
            print(f"Count: {count}, Limit: {scrolls}")
            if count >scrolls:
                print("Scrolling stopped after 10 iterations")
                break
            print(f"Scrolling... {count} iterations")

            callback(driver)
            

    except Exception as e:
        # logs.log_error(f"Error occurred while scrolling: {e}")
        pass
