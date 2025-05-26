# from airflow.decorators import task
from utils.downloader import download_video
from config import Config
import os
import json

import sys
sys.path.append('/opt/airflow/dags')

from app.core.database_utils import create_pending_video, update_video_status, get_info_by_user_id
from app.worker.schema import TaskStatus
from dags.utils.get_id import extract_id

# @task
def x_videos_scraper(id = "elonmusk",downloads = 5):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(storage_state="dags/utils/state.json")
        page = context.new_page() 

        # Truy cập trang cá nhân
        page.goto(f"https://x.com/{id}/media", timeout=15000)

        page.wait_for_timeout(5000)  # chờ page load

        hrefs = []

        results = get_info_by_user_id(platform="x", user_id=id)

        # Cuộn xuống để tải thêm tweets
        while len(hrefs) < downloads:
        # for i in range(scrolls):
            # print(f"Scrolling down... {i}")
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
                    
        for result in results:
            if result.url in hrefs:
                hrefs.remove(result.url)
        print(f"Remaining new videos: {len(hrefs)}")

        hrefs = hrefs[:downloads]  # Giới hạn số lượng video mới lấy về
        print(f"Total new videos to process: {len(hrefs)}")

        new_links = set(hrefs)

        print(f"New videos: {len(new_links)}")

        context.close()
        browser.close()

        return {'id': id, 'new_links': new_links}

 
