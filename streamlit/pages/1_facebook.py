import streamlit as st
from database_utils import get_distinct_user_ids_from_db, get_info_by_user_id, delete_user_by_id
from send_request import send_request, retry_task
from platform_utils import (
    show_user_info,
    delete_user_dialog,
    display_users,
    track_dag_status_ui,
    get_task_status_from_log
    # final_result
)
import os
import re

@st.dialog("Xóa người dùng Facebook", width="large")
def delete_user(user_id):
    delete_user_dialog(user_id, "facebook", delete_user_by_id)

# def get_task_status_from_log(log_file_path, attempt=1):
#     if not os.path.exists(log_file_path):
#         return "", "", "chưa chạy"
#     with open(log_file_path, "r") as f:
#         content = f.read()
#         if "Done" in content:
#             if "Returned value was: [" in content:
#                 downloaded = content.count("Downloaded video")
#                 new_videos = downloaded
#             else:
#                 match = re.search(r"Number of downloads to process:\s*(\d+)", content)
#                 if match:
#                     new_videos = match.group(1)
#                     downloaded = content.count("Processing audio file")
#                 else:
#                     match = re.search(r"New videos:\s*(\d+)", content)
#                     if match:
#                         new_videos = match.group(1)
#                         downloaded = content.count("Downloaded successfully")
#                     else:
#                         new_videos = 0
#                         downloaded = 0
#             return new_videos, downloaded, "thành công"
#         elif "Task is not able to be run" in content or "Error" in content and "unable to obtain file audio codec with ffprobe" not in content and "Error transcripting video" not in content and "WARNING - ERROR" not in content:
#             return "", "", "thất bại"
#         elif "Downloading" in content or "Processing" in content or "Extracting videos" in content:
#             if "Starting batch download..." in content:
#                 downloaded = content.count("Downloaded successfully")
#             else:
#                 match = re.search(r"Number of downloads to process:\s*(\d+)", content)
#                 if match:
#                     downloaded = content.count("Processing audio with duration")
#                 else:
#                     downloaded = 0
#             return "", downloaded, "đang chạy"
#         elif "Scrolling" in content:
#             return "", "", "đang tìm video"
#         else:
#             return "", "", "chưa chạy"

def display_facebook_users():
    display_users(
        "facebook",
        get_distinct_user_ids_from_db,
        lambda user_id: show_user_info(user_id, "facebook", get_info_by_user_id),
        delete_user,
        link_format="[https://www.facebook.com/{0}](https://www.facebook.com/{0})"
    )

@st.dialog("Thêm người dùng Facebook", width="large")
def add_facebook_user():
    st.write("Thêm người dùng Facebook vào cơ sở dữ liệu")
    user_id = st.text_input("Nhập user_id Facebook", placeholder="Nhập user_id Facebook")
    count = st.number_input("Nhập số lượng video cần tải về", min_value=1, max_value=100, value=5, step=5)
    if st.button("Thêm"):
        if user_id:
            with st.spinner('Đang gửi yêu cầu tới Airflow...'):
                success, message, dag_run_id = send_request(id=user_id, count=count, platform="facebook")
                if success:
                    st.success(message)
                    st.session_state['dag_run_id'] = dag_run_id
                else:
                    st.error(message)
        else:
            st.warning("Vui lòng nhập user_id Facebook.")

    dag_id = "facebook_videos_scraper_dag"
    dag_run_id = st.session_state.get('dag_run_id', None)
    if dag_run_id is None:
        st.warning("Chưa có DAG nào được chạy. Vui lòng gửi yêu cầu trước.")
        st.stop()

    # to_display = final_result(get_task_status_from_log, dag_id, dag_run_id)

    track_dag_status_ui(
        dag_id,
        dag_run_id,
        user_id,
        get_info_by_user_id,
        lambda uid: show_user_info(uid, "facebook", get_info_by_user_id),
        get_task_status_from_log,
        lambda dag_id, dag_run_id, task_id: retry_task(dag_id, dag_run_id, task_id=task_id)
    )

st.title('Danh sách người dùng Facebook')
display_facebook_users()
if st.button("Thêm người dùng Facebook"):
    add_facebook_user()