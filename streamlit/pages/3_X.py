import streamlit as st
from database_utils import get_distinct_user_ids_from_db, get_info_by_user_id, delete_user_by_id
from send_request import send_request, stop_dag
from platform_utils import (
    show_user_info,
    delete_user_dialog,
    display_users,
    get_task_status_from_log,
    track_dag_status_ui,
)

@st.dialog("Xóa người dùng X", width="large")
def delete_user(user_id):
    delete_user_dialog(user_id, "X", delete_user_by_id)

def display_x_users():
    display_users(
        "X",
        get_distinct_user_ids_from_db,
        lambda user_id: show_user_info(user_id, "X", get_info_by_user_id),
        delete_user,
        link_format="[https://www.x.com/@{0}](https://www.x.com/@{0})"
    )

@st.dialog("Thêm người dùng X", width="large")
def add_x_user():
    st.write("Thêm người dùng X vào cơ sở dữ liệu")
    user_id = st.text_input("Nhập user_id X", placeholder="Nhập user_id X")
    count = st.number_input("Nhập số lượng video cần tải về", min_value=1, max_value=100, value=5, step=5)
    if st.button("Thêm"):
        if user_id:
            with st.spinner('Đang gửi yêu cầu tới Airflow...'):
                success, message, dag_run_id = send_request(id=user_id, count=count, platform="x")
                if success:
                    st.success(message)
                    st.session_state['dag_run_id'] = dag_run_id
                else:
                    st.error(message)
        else:
            st.warning("Vui lòng nhập user_id X.")

    dag_id = "x_videos_scraper_dag"
    dag_run_id = st.session_state.get('dag_run_id', None)
    if dag_run_id is None:
        st.warning("Chưa có DAG nào được chạy. Vui lòng gửi yêu cầu trước.")
        st.stop()

    track_dag_status_ui(
        dag_id,
        dag_run_id,
        user_id,
        get_info_by_user_id,
        lambda uid: show_user_info(uid, "X", get_info_by_user_id),
        stop_dag,
        get_task_status_from_log
    )

st.title('Danh sách người dùng X')
display_x_users()
if st.button("Thêm người dùng X"):
    add_x_user()