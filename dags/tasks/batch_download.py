# from concurrent.futures import ThreadPoolExecutor
# from functools import partial
# from tqdm import tqdm
# from ..utils.downloader import download_video
# import asyncio
# from tqdm.asyncio import tqdm_asyncio
# from ..utils.download_tiktok import main as download_tiktok
from app.worker.schema import TaskStatus
from app.core.database_utils import create_pending_video, update_video_status
from config import Config
from utils.get_id import extract_id
from utils.downloader import download_video

def batch_download(**context):
    """Read URLs from a text file and download them concurrently."""

    print("Starting batch download...")

    platform = context.get("platform", "tiktok")
    ti = context["ti"]
    id, urls = ti.xcom_pull(task_ids="get_links_task").values()
    if not urls:
        print("No URLs to download.")
        return []

    results = []

    for link in urls:
        video_id = extract_id(link)
        # user_id = extract_user_id(link)
        task_id = create_pending_video(video_id, id, link, platform=platform)
        file_path = download_video(link, Config.DOWNLOAD_DIRECTORY)
        if file_path:
            update_video_status(video_id, TaskStatus.PROCESSING.value, platform=platform)
            result = {
                "video_id": video_id,
                "file_path": file_path,
            }
            print(f"Downloaded video {result['video_id']} to {result['file_path']}")
            results.append(result)                    
            
        else:
            update_video_status(video_id, TaskStatus.FAILURE.value, platform=platform, logs="Error downloading video")
        
    print(f"Downloaded {len(results)} new videos.")
    return results

# if platform == "tiktok":

    #     # async with TikTokApi() as api:
    #     #     await api.create_sessions(ms_tokens=ms_tokens, num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
    #     tasks = [download_tiktok(url) for url in urls]
    #     tqdm_asyncio.gather(*tasks, desc="Tiktok Batch")
    # else:
    #     with ThreadPoolExecutor() as executor:
    #         list(
    #             tqdm(
    #                 executor.map(partial(download_video, download_directory=download_directory), urls),
    #                 total=len(urls),
    #                 desc="Facebook/Youtube/Tiktok/Instagram Batch",
    #             )
    #         )

    # print("Download complete.")