import streamlit as st
from database_utils import get_distinct_user_ids_from_db, get_info_by_user_id, delete_user_by_id
from send_request import send_request, retry_task
import pandas as pd
import time
from platform_utils import (
    show_user_info,
    delete_user_dialog,
    display_users,
    get_task_status_from_log,
    track_dag_status_ui,  
    # final_result
)

@st.dialog("Xóa người dùng TikTok", width="large")
def delete_user(user_id):
    delete_user_dialog(user_id, "tiktok", delete_user_by_id)

def display_tiktok_users():
    display_users(
        "tiktok",
        get_distinct_user_ids_from_db,
        lambda user_id: show_user_info(user_id, "tiktok", get_info_by_user_id),
        delete_user,
        link_format="[https://www.tiktok.com/@{}](https://www.tiktok.com/@{})"
    )

@st.dialog("Thêm người dùng TikTok", width="large")
def add_tiktok_user():
    st.write("Thêm người dùng TikTok vào cơ sở dữ liệu")
    user_id = st.text_input("Nhập user_id TikTok", placeholder="Nhập user_id TikTok")
    count = st.number_input("Nhập số lượng video cần tải về", min_value=1, max_value=100, value=5, step=5)
    if st.button("Thêm"):
        if user_id:
            with st.spinner('Đang gửi yêu cầu tới Airflow...'):
                success, message, dag_run_id = send_request(id=user_id, count=count, platform="tiktok")
                if success:
                    st.success(message)
                    st.session_state['dag_run_id'] = dag_run_id
                else:
                    st.error(message)
        else:
            st.warning("Vui lòng nhập user_id TikTok.")

    dag_id = "tiktok_videos_scraper_dag"
    dag_run_id = st.session_state.get('dag_run_id', None)
    if dag_run_id is None:
        st.warning("Chưa có DAG nào được chạy. Vui lòng gửi yêu cầu trước.")
        st.stop()

    # to_display = final_result(get_task_status_from_log, dag_id, dag_run_id)        

    # Sử dụng hàm tiện ích mới
    track_dag_status_ui(
        dag_id,
        dag_run_id,
        user_id,
        get_info_by_user_id,
        lambda uid: show_user_info(uid, "tiktok", get_info_by_user_id),
        get_task_status_from_log,        
        lambda dag_id, dag_run_id, task_id: retry_task(dag_id, dag_run_id, task_id=task_id)
    )

st.title('Danh sách người dùng TikTok')
display_tiktok_users()
if st.button("Thêm người dùng TikTok"):
    add_tiktok_user()