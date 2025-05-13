from airflow.decorators import task
from dags.app.worker.schema import TaskStatus
from utils.downloader import batch_download_from_file, download_video
from dags.tasks.get_transcript import audio_to_transcript
from config import Config

import sys
sys.path.append('/opt/airflow/dags')

from app.core.database_utils import create_pending_video, get_all_videos_from_db, update_video_status
from dags.utils.get_id import extract_id

# @task.virtualenv(
#     task_id="virtualenv_python", requirements=["TikTokApi==7.1.0"], system_site_packages=False
# )
@task

def tiktok_videos_scraper(id = "therock",count = 10, ms_tokens=None, TIKTOK_ERROR_FILE_PATH= "data/scraped_data/tiktok.txt", TIKTOK_FILE_PATH="data/scraped_data/tiktok.txt", DOWNLOAD_DIRECTORY="media"):
    from TikTokApi import TikTokApi
    import asyncio
    import os
    # import json
    ms_tokens = os.environ.get(
    "ms_token", None
    )  # set your own ms_token, think it might need to have visited a profile
    # ms_token = Config.MS_TOKENS
    
    async def user_example():
        async with TikTokApi() as api:
            # Đổi ms_tokens nếu bị lỗi chạy headless
            videos=[]
            new_links = []
            try:
                await api.create_sessions(ms_tokens=['azquqBjM67uB1DOXOvXJuaQxP1vQD8Ez_a8kDxBXNDBbLFFRE4KWUDuX-l0OjQvpgbE_dYsreYMw739sg14g8lycqGHMkEzwuWRN-L0ldYWWGwWoYs4Gw8MDxAWhEscDMqFxCSFgB3ayJ_KUoLceFA=='], 
                                        num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
                user = api.user(f"{id}")
                async for video in user.videos(count=count):
                    print(f"https://www.tiktok.com/@{id}/video/"+video.as_dict['id'])
                    videos.append(f"https://www.tiktok.com/@{id}/video/"+video.as_dict['id'])     

                results = get_all_videos_from_db(platform="tiktok")
                for result in results:
                    if result.url in videos:
                        videos.remove(result.url)
                print(f"Remaining new videos: {len(videos)}")

                new_links = set(videos)

                print(f"New videos: {len(new_links)}")
            except Exception as e:
                print(f"Error in TikTok API: {e}")
                return []
            results = []

            for link in new_links:
                video_id = extract_id(link)
                task_id = create_pending_video(video_id, link, platform="tiktok")
                file_path = download_video(link, Config.DOWNLOAD_DIRECTORY)
                if file_path:
                    update_video_status(video_id, TaskStatus.PROCESSING.value, platform="tiktok")
                    result = {
                        "video_id": video_id,
                        "file_path": file_path,
                    }
                    print(f"Downloaded video {result['video_id']} to {result['file_path']}")
                    results.append(result)                    
                    
                else:
                    update_video_status(video_id, TaskStatus.FAILURE.value, platform="tiktok", logs="Error downloading video")
                
            print(f"Downloaded {len(results)} new videos.")
            return results
    #         # batch_download_from_file(TIKTOK_FILE_PATH, DOWNLOAD_DIRECTORY, platform="tiktok")
    # asyncio.run(user_example())
    results = asyncio.run(user_example())
    return results  # thêm dòng này
