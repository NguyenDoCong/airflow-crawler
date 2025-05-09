from airflow.decorators import task
from utils.downloader import batch_download_from_file, download_video
from config import Config
import os
import json

import sys
sys.path.append('/opt/airflow/dags')

from app.core.database_utils import create_pending_video, get_all_videos_from_db, update_video_status
from app.worker.schema import TaskStatus
from dags.utils.get_id import extract_id

@task
def x_videos_scraper(id = "elonmusk", scrolls = 5):
    from playwright.sync_api import sync_playwright

    # storage_state_path = "dags/utils/state.json"
    # use_storage_state = False
    # if not os.path.exists(storage_state_path):
    #     os.makedirs(os.path.dirname(storage_state_path), exist_ok=True)
    # try:
    #     with open(storage_state_path, "r", encoding="utf-8") as f:
    #         json.load(f)
    #     use_storage_state = True
    # except Exception as e:
    #     print(f"Error loading storage_state.json: {e}")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(storage_state="dags/utils/state.json")
        # context = browser.new_context()
        # if use_storage_state:
        #     context = browser.new_context(storage_state=storage_state_path)
        # else:
        #     context = browser.new_context()
        page = context.new_page() 

        # Truy cập trang cá nhân
        page.goto(f"https://x.com/{id}/media", timeout=15000)

        page.wait_for_timeout(5000)  # chờ page load

        hrefs = []
        # Cuộn xuống để tải thêm tweets
        for i in range(scrolls):
            print(f"Scrolling down... {i}")
            old_links = set(hrefs)
                
            # Cuộn bằng JS
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            page.wait_for_timeout(5000)

            # Kiểm tra tất cả <a> sau khi load
            for element in page.locator("a").all():
                link = element.get_attribute("href")
                if link and "/video/" in link:
                    full_link = f"https://x.com{link}"
                    if full_link not in hrefs:
                        hrefs.append(full_link)
                        print(full_link)

            if set(hrefs) == old_links:
                break
                    
        results = get_all_videos_from_db()
        for result in results:
            if result.url in hrefs:
                hrefs.remove(result.url)
        print(f"Remaining new videos: {len(hrefs)}")

        new_links = set(hrefs)

        print(f"New videos: {len(new_links)}")

        for link in new_links:
            video_id = extract_id(link)
            task_id = create_pending_video(video_id, link, platform="x")
            result = download_video(link, Config.DOWNLOAD_DIRECTORY)
            if result:
                update_video_status(video_id, TaskStatus.DOWNLOADED.value, platform="x")

        context.close()
        browser.close()
    # batch_download_from_file(Config.X_FILE_PATH, Config.DOWNLOAD_DIRECTORY, platform="x")
