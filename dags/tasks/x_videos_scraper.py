from airflow.decorators import task
from utils.downloader import download_video
from config import Config
import os
import json

import sys
sys.path.append('/opt/airflow/dags')

from app.core.database_utils import create_pending_video, get_all_videos_from_db, update_video_status
from app.worker.schema import TaskStatus
from dags.utils.get_id import extract_id

@task
def x_videos_scraper(id = "elonmusk",scrolls = 5):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(storage_state="dags/utils/state.json")
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

        results = []

        for link in new_links:
            try:
                video_id = extract_id(link)
                task_id = create_pending_video(video_id, link, platform="x")
                file_path = download_video(link, Config.DOWNLOAD_DIRECTORY)
                if file_path:
                    update_video_status(video_id, TaskStatus.PROCESSING.value, platform="x")
                    result = {
                        "video_id": video_id,
                        "file_path": file_path,
                    }
                    print(f"Downloaded video {result['video_id']} to {result['file_path']}")
                    results.append(result)                    
                    
                else:
                    update_video_status(video_id, TaskStatus.FAILURE.value, platform="x", logs="Error downloading video")
            except Exception as e:
                print(f"Error downloading video {link}: {e}")
                # update_video_status(video_id, TaskStatus.FAILURE.value, platform="x", logs="Error downloading video")
                continue
            
        print(f"Downloaded {len(results)} new videos.")

        context.close()
        browser.close()

        return results

    # batch_download_from_file(Config.X_FILE_PATH, Config.DOWNLOAD_DIRECTORY, platform="x")
