import os
class Config:
    """
    Configuration class for the application.
    """

    # Scrolling
    SCROLL_PAUSE_TIME = 3
    MAX_CONSECUTIVE_SCROLLS = 1

    # Download directory
    DOWNLOAD_DIRECTORY = "media"
    downloaded_videos_file = "scraped_data/downloaded_videos.txt"

    # Facebook login"
    FACEBOOK_EMAIL = "wachterson34@gmail.com"
    FACEBOOK_PASSWORD = "mqsolutions123,"
    COOKIES_FILE_PATH = "cookies/fb_cookies.json"

    # # Instagram login
    # INSTAGRAM_FILE_PATH = "instagram_cookies.json"
    INSTAGRAM_SESSIONID_VALUE = "51375314644%3AuibAf9idJuFKhk%3A16%3AAYfzVQuj1x_p7Alj2x3RpVzhKNy73XNzdH1vFeKhpQ"

    # TikTok 
    TIKTOK_FILE_PATH= '{{ "data/scraped_data/tiktok.txt" }}'
    TIKTOK_ERROR_FILE_PATH= '{{ "data/scraped_data/tiktok_error.txt" }}'
    MS_TOKENS = ['azquqBjM67uB1DOXOvXJuaQxP1vQD8Ez_a8kDxBXNDBbLFFRE4KWUDuX-l0OjQvpgbE_dYsreYMw739sg14g8lycqGHMkEzwuWRN-L0ldYWWGwWoYs4Gw8MDxAWhEscDMqFxCSFgB3ayJ_KUoLceFA==']
    # X 
    X_FILE_PATH = "scraped_data/x.txt"
    # facebook
    FACEBOOK_FILE_PATH = "scraped_data/facebook.txt"

    # instagram
    INSTAGRAM_FILE_PATH = "scraped_data/instagram.txt"

    # logs
    LOG_FILE_PATH = "logs.log"

    # Json
    JSON_FILE_PATH = "scraped_data/"

    # # Facebook paths
    # FRIEND_LIST_URL = "friends"
    # WORK_AND_EDUCATION_URL = "about_work_and_education"
    # PLACES_URL = "about_places"
    # FAMILY_URL = "about_family_and_relationships"
    CONTACT_URL = "about_contact_and_basic_info"

    # Save to json
    INDENT = 4
    ENSURE_ASCII = False

    GMAIL = "nguyen.do.cong@mqsolutions.com.vn"
    GMAIL_PASSWORD = "123456789"
    X_USERNAME = "CongNguyen62411"
    X_PASSWORD = "mqsolutions123"

    # Database configuration
    USER_DATABASE       = os.environ.get("USER_DATABASE", "postgres")
    PASSWORD_DATABASE   = os.environ.get("PASSWORD_DATABASE", "postgres")
    HOST_DATABASE       = os.environ.get("HOST_DATABASE", "postgres")
    PORT_DATABASE       = os.environ.get("PORT_DATABASE", "5432")
    NAME_DATABASE       = os.environ.get("NAME_DATABASE", "postgres")
    URL_DATABASE        = f"postgresql://{USER_DATABASE}:{PASSWORD_DATABASE}@{HOST_DATABASE}:{PORT_DATABASE}/{NAME_DATABASE}"