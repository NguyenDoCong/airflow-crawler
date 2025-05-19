import re

# Các regex pattern cho từng nền tảng
patterns = {
    'x': r"x\.com/.+?/status/(\d+)",
    'tiktok': r"tiktok\.com/@.+?/video/(\d+)",
    'instagram': r"instagram\.com/.+?/reel/([A-Za-z0-9_-]+)",
    'facebook': r"facebook\.com/.+?/videos/(?:[^/]+/)?(\d+)"
}

# Hàm lấy ID theo từng nền tảng
def extract_id(url):
    result = None
    for platform, pattern in patterns.items():
        match = re.search(pattern, url)
        if match:
            result = match.group(1)
            break
    if not result:
        print(f"Không nhận dạng được URL: {url}")
    return result

def extract_user_id(url):

    if "x.com" in url or "twitter.com" in url:
        match = re.search(r"x\.com/([^/]+)/status", url)
        if match:
            result = match.group(1)

    elif "facebook.com" in url:
        match = re.search(r"facebook\.com/([^/]+)/videos", url)
        if match:
            result = match.group(1)

    elif "tiktok.com" in url:
        match = re.search(r"tiktok\.com/@([^/]+)/video", url)
        if match:
            result = match.group(1)

    elif "instagram.com" in url:
        match = re.search(r"instagram\.com/([^/]+)/reel", url)
        if match:
            result = match.group(1)

    else:
        result = None

    return result

def __main__():
    video_id = extract_id("https://x.com/elonmusk/status/1916035259990479114/video/1")
    if video_id:
        print(f"Video ID: {video_id}")

if __name__ == "__main__":
    __main__()
