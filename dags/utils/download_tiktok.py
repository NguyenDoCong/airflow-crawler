import json
import os
import random
from bs4 import BeautifulSoup
import requests
import time
from playwright.async_api import async_playwright

async def save_cookies(video_url, cookies_filename="dags/utils/cookies.json", user_agent_filename="dags/utils/user_agent.txt"):
    print("Start saving cookies...")
    async with async_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page.goto("https://www.tiktok.com", timeout=60000)
        page.wait_for_load_state("networkidle")

        cookies = context.cookies()
        with open(cookies_filename, 'w') as f:
            json.dump(cookies, f)

        user_agent = page.evaluate("navigator.userAgent")

        if not os.path.exists(user_agent_filename):
            os.makedirs(os.path.dirname(user_agent_filename), exist_ok=True)

        with open(user_agent_filename, "w") as f:
            f.write(user_agent)

        print(f"✅ Cookies saved to {cookies_filename}.")
        browser.close()


def is_cookie_valid(response):
    return response.status_code == 200 and response.content


def get_url(video_url, is_music=True, cookies_filename="dags/utils/cookies.json", user_agent_filename="dags/utils/user_agent.txt"):
    try:
        with open(cookies_filename, 'r') as f:
            cookies_data = json.load(f)
            COOKIES = {cookie["name"]: cookie["value"] for cookie in cookies_data}
        
        if not os.path.exists(user_agent_filename):
            os.makedirs(os.path.dirname(user_agent_filename), exist_ok=True)
        with open(user_agent_filename, "r") as f:
            user_agent = f.read().strip()
        HEADERS = {
            'User-Agent': user_agent,
            'Referer': 'https://www.tiktok.com/',
        }
        session = requests.Session()
        response = session.get(video_url, headers=HEADERS, cookies=COOKIES, timeout=10)

        if not is_cookie_valid(response):
            print("❌ Cookies expired. Refreshing with Playwright...")
            save_cookies(video_url, cookies_filename, user_agent_filename)
            with open(cookies_filename, 'r') as f:
                cookies_data = json.load(f)
                COOKIES = {cookie["name"]: cookie["value"] for cookie in cookies_data}
            response = session.get(video_url, headers=HEADERS, cookies=COOKIES, timeout=10)

        response.raise_for_status()
    except Exception as e:
        raise Exception(f"Error getting video page: {e}")

    soup = BeautifulSoup(response.content, 'html.parser')
    script_tag = soup.find('script', {
        'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__',
        'type': 'application/json'
    })

    if not script_tag:
        raise ValueError("Could not find the JSON script tag in the page.")

    try:
        data = json.loads(script_tag.string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON data: {e}")

    scope = data.get('__DEFAULT_SCOPE__', {})
    for section in scope.values():
        if not isinstance(section, dict):
            continue
        item_info = section.get('itemInfo', {})
        item_struct = item_info.get('itemStruct')
        if item_struct:
            return item_struct['music']['playUrl'] if is_music else item_struct['video']['downloadAddr']

    raise ValueError("Direct URL not found in the provided data.")


def download_file(link, url_to_download, is_music=True):
    id = link.split("/")[-1]
    if not os.path.exists('media'):
        os.mkdir('media')

    file_directory = f'media/{id}.mp3' if is_music else f'media/{id}.mp4'

    with open(file_directory, 'wb') as file_to_save:
        file_content = requests.get(url_to_download).content
        file_to_save.write(file_content)

    print(f'✅ File downloaded in {file_directory}')
    return file_directory


def main(link, is_music=True, cookies_filename="dags/utils/cookies.json", user_agent_filename="dags/utils/user_agent.txt"):
    print('Getting direct link...', link)
    # Check if cookies file exists, if not, save cookies
    if not os.path.exists(cookies_filename) or not os.path.exists(user_agent_filename):
        print('❌ Cookies not found. Saving cookies...')
        save_cookies(link)
    # Check content of cookies file, if empty, save cookies
    # if os.path.getsize(cookies_filename) == 0 or os.path.getsize(user_agent_filename) == 0:
    #     print('❌ Cookies file is empty. Saving cookies...')
    #     save_cookies(link)
    download_url = get_url(link, is_music)
    print('✅ Direct link:', download_url)
    download_file(link, download_url, is_music)
    # file_dir = download_file(download_url, is_music)


if __name__ == '__main__':
    urls = [
        'https://www.tiktok.com/@michaelslicks/video/7472495819627810091',
        'https://www.tiktok.com/@fvqkrv/video/7456979203972435222'
    ]

    for i in range(2):
        print(f'Iteration {i}')
        try:
            url = random.choice(urls)
            start_time = time.time()
            main(url)
            print('⏱ Time taken: {} seconds'.format(time.time() - start_time))
        except Exception as e:
            print(f'❌ Error: {e}')
