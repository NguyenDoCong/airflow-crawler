# from airflow.decorators import task
from dags.app.worker.schema import TaskStatus
# from utils.downloader import download_video
from config import Config

import sys
sys.path.append('/opt/airflow/dags')

from app.core.database_utils import get_info_by_user_id
# from dags.utils.get_id import extract_id

# @task.virtualenv(
#     task_id="virtualenv_python", requirements=["TikTokApi==7.1.0"], system_site_packages=False
# )
# @task

def tiktok_videos_scraper(id = "therock",count = 10, ms_tokens=None, DOWNLOAD_DIRECTORY="data"):
    from TikTokApi import TikTokApi
    import asyncio
    import os
    # from batch_download import batch_download
    # import json
    ms_tokens = os.environ.get(
    "ms_token", None
    )  # set your own ms_token, think it might need to have visited a profile
    ms_tokens = Config.MS_TOKENS
    
    async def user_template():
        async with TikTokApi() as api:
            # Đổi ms_tokens nếu bị lỗi chạy headless
            videos=[]
            new_links = []
            try:
                await api.create_sessions(ms_tokens=ms_tokens, 
                                        num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
                user = api.user(f"{id}")
                async for video in user.videos(count=count):
                    print(f"https://www.tiktok.com/@{id}/video/"+video.as_dict['id'])
                    videos.append(f"https://www.tiktok.com/@{id}/video/"+video.as_dict['id'])     

                results = get_info_by_user_id(platform="tiktok", user_id=id)
                for result in results:
                    if result.url in videos:
                        videos.remove(result.url)
                # print(f"Remaining new videos: {len(videos)}")

                new_links = set(videos)

                print(f"New videos: {len(new_links)}")
                return {'id': id, 'new_links': new_links}
            except Exception as e:
                print(f"Error in TikTok API: {e}")
                return []
            

            # results = []

            # for link in new_links:
            #     video_id = extract_id(link)
            #     # user_id = extract_user_id(link)
            #     task_id = create_pending_video(video_id, id, link, platform="tiktok")
            #     file_path = download_video(link, Config.DOWNLOAD_DIRECTORY)
            #     if file_path:
            #         update_video_status(video_id, TaskStatus.PROCESSING.value, platform="tiktok")
            #         result = {
            #             "video_id": video_id,
            #             "file_path": file_path,
            #         }
            #         print(f"Downloaded video {result['video_id']} to {result['file_path']}")
            #         results.append(result)                    
                    
            #     else:
            #         update_video_status(video_id, TaskStatus.FAILURE.value, platform="tiktok", logs="Error downloading video")
                
            # print(f"Downloaded {len(results)} new videos.")
            # return results
    # asyncio.run(user_example())
    # results = asyncio.run(user_template())
    # return results  
    return asyncio.run(user_template())