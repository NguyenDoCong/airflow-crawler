
import os
# import sys
import csv
import time
import json
# import shutil
import yt_dlp
import logging
import requests
# import instaloader
from tqdm import tqdm
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from config import Config
from functools import partial
import re
from dags.utils.get_id import extract_id

import sys
# sys.path.insert(1, 'src/utils')
sys.path.append('/opt/airflow/dags')

# ---------------------------------
# Logging Setup
# ---------------------------------
logging.basicConfig(
    filename="downloader.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ---------------------------------
# Load Configuration
# ---------------------------------
# CONFIG_FILE = "config.json"
# DEFAULT_CONFIG = {
#     "default_format": "show_all",
#     "download_directory": "media",
#     "history_file": "download_history.csv",
#     "mp3_quality": "192",
# }


# def load_config():
#     """Load or create configuration file safely."""
#     if not os.path.exists(CONFIG_FILE):
#         with open(CONFIG_FILE, "w") as f:
#             json.dump(DEFAULT_CONFIG, f, indent=4)

#     try:
#         with open(CONFIG_FILE, "r") as f:
#             return json.load(f)
#     except (json.JSONDecodeError, IOError):
#         logging.error("Invalid config file. Resetting to defaults.")
#         with open(CONFIG_FILE, "w") as f:
#             json.dump(DEFAULT_CONFIG, f, indent=4)
#         return DEFAULT_CONFIG


# config = load_config()
# download_directory = config["download_directory"]
# history_file = config["history_file"]
# mp3_quality = config["mp3_quality"]

download_directory = Config.DOWNLOAD_DIRECTORY

os.makedirs(download_directory, exist_ok=True)  # Ensure download directory exists


# ---------------------------------
# Utility Functions
# ---------------------------------
def check_internet_connection():
    """Check if the system has an active internet connection."""
    try:
        requests.head("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


def ensure_internet_connection():
    """Ensure that an internet connection is active before proceeding."""
    while not check_internet_connection():
        print("\nNo internet connection. Retrying in 5 seconds...")
        time.sleep(5)
    print("Internet connection detected. Proceeding...")


# def log_download(url, status):
#     """Log the download status in history and log file."""
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     with open(history_file, "a+", newline="") as f:
#         csv.writer(f).writerow([url, status, timestamp])
#     logging.info(f"Download status for {url}: {status}")


# def get_unique_filename(filename):
#     """Ensure downloaded files are renamed if duplicates exist."""
#     base, ext = os.path.splitext(filename)
#     counter = 1
#     while os.path.exists(filename):
#         filename = f"{base} ({counter}){ext}"
#         counter += 1
#     return filename


# def extract_id(url):
    
#     if "x.com" in url or "twitter.com" in url:
#         match = re.search(r"status/(\d+)", url)
#         if match:
#             id= match.group(1)
    
#     elif "facebook.com" in url:
#         match = re.search(r"videos/(\d+)", url)
#         if match:
#             id= match.group(1)
    
#     elif "tiktok.com" in url:
#         match = re.search(r"video/(\d+)", url)
#         if match:
#             id= match.group(1)

#     elif "instagram.com" in url:
#         match = re.search(r'/reel/([A-Za-z0-9_-]+)/?', url)
#         if match:
#             id= match.group(1)
#     else:
#         id= match.group(1)
    
#     return id 

def download_video(url, download_directory):
    """Download a YouTube or TikTok video with user-selected format (ensuring video has audio)."""
    ensure_internet_connection()
    try:
        id = extract_id(url)
    except Exception as e:
        print(f"Error extracting video ID: {e}")
        return None

    print(f"Downloading video from {id}...")
    try:        
        ydl_opts = {"listformats": True}
        ydl_opts = {
            'nocheckcertificate': True,
            'quiet': False,

            'http_headers': {
                # Dòng này sẽ được tự động cấu hình đúng nếu dùng `--impersonate`, nhưng ta cũng có thể chỉ định thủ công nếu muốn
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            },
            # 'compat_opts': ['client=youtube-web:Chrome'],  # chính là tương đương `--impersonate firefox`
        }

        file_path = os.path.join(download_directory, f"{id}")
        ydl_opts = {

            "format": "bestaudio/best",
            'outtmpl': file_path,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
            ],
        }

        # Download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # print("-------------------------------------------------")
            ydl.download([url])
            # log_download(url, "Success")
            print(f"\n\033[1;32mDownloaded successfully:\033[0m {id}")       

        return file_path + ".mp3"

    except Exception as e:
        print(f"\n\033[1;31mError downloading video using yt-dlp:\033[0m {e}")

        try:
        
            url = f"https://www.tikwm.com/video/music/{id}.mp3"
            file = requests.get(url)
            file_path = os.path.join(download_directory, f"{id}.mp3")
            with open(file_path, "wb") as f:
                f.write(file.content)

            return file_path
        except Exception as e:
            print(f"\n\033[1;31mError downloading video using requests:\033[0m {e}")
            # log_download(url, "Failed")
            return None

if __name__ == "__main__":
    download_video("https://www.tiktok.com/@theanh28entertainment/video/7496340302253362439")