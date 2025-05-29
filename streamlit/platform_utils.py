import streamlit as st
import pandas as pd
import os
import re
import time
from send_request import retry_task
from monitoring import AirflowAPI

def show_user_info(user_id, platform, get_info_by_user_id, to_display=None):
    user_detail = get_info_by_user_id(user_id, platform=platform)
    st.markdown("---")
    if not user_detail:
        st.write("Không có dữ liệu người dùng.")
        return
    display_data = []
    for item in user_detail:
        display_data.append({
            "url": getattr(item, "url", "N/A"),
            "transcript": getattr(item, "transcript", "")
        })

    infos = pd.DataFrame(display_data)
    if isinstance(to_display, int) and to_display > 0:
        infos = infos.head(to_display)
        st.write(f"Số kết quả: {len(infos)}/{len(display_data)}")
    else:
        st.write(f"Số kết quả: {len(infos)}")
    st.markdown(infos.to_html(escape=False), unsafe_allow_html=True)

def delete_user_dialog(user_id, platform, delete_user_by_id):
    st.write(f"Xóa người dùng {platform} khỏi cơ sở dữ liệu")
    if user_id:
        st.write(f"Bạn có chắc chắn muốn xóa người dùng {user_id} không?")
        if st.button("Xóa"):
            delete_user_by_id(user_id, platform=platform)
            st.success(f"Đã xóa người dùng {user_id} khỏi cơ sở dữ liệu.")
            st.rerun()
    else:
        st.warning("Không có người dùng nào được chọn.")

def display_users(platform, get_distinct_user_ids_from_db, show_user_info_func, delete_user_func, link_format):
    user_ids = get_distinct_user_ids_from_db(platform=platform)
    users = pd.DataFrame(columns=["STT", "user_id", "link"])
    if user_ids:
        for idx, user_id in enumerate(user_ids, start=1):
            user_id = user_id[0]
            if user_id is not None:
                user_id = str(user_id)
                user_link = link_format.format(user_id, user_id)
                users = pd.concat([
                    users,
                    pd.DataFrame([{"STT": idx, "user_id": user_id, "link": user_link}])
                ], ignore_index=True)
            else:
                st.warning("Không có user_id nào trong cơ sở dữ liệu.")
                return

        header = st.columns([1, 3, 5, 2])
        header[0].write("STT")
        header[1].write("User ID")
        header[2].write("Link")
        header[3].write("Xóa")

        @st.dialog("Chi tiết người dùng", width="large")
        def show_user_info_dialog(user_id):
            show_user_info_func(user_id)

        for index, row in users.iterrows():
            cols = st.columns([1, 3, 5, 2])
            cols[0].write(row["STT"])
            if cols[1].button(row["user_id"], key=f"user_{index}"):
                st.session_state["selected_user_id"] = row["user_id"]
                show_user_info_dialog(row["user_id"])
            cols[2].markdown(row["link"], unsafe_allow_html=True)
            if cols[3].button("Xóa", key=f"btn_{index}"):
                delete_user_func(row["user_id"])
    else:
        st.write("Không có người dùng nào trong cơ sở dữ liệu.")

def get_task_status_from_log(log_file_path):
    # Đổi tên file log theo attempt
    # log_file_path = re.sub(r"attempt=\d+\.log", f"attempt={attempt}.log", log_file_path)
    if not os.path.exists(log_file_path):
        return "", "", "chưa chạy", ""
    with open(log_file_path, "r") as f:
        content = f.read()
        if "Done" in content:
            match = re.search(r"Downloaded\s+(\d+)\s+new videos", content)
            if match:
                new_videos = match.group(1)
                downloaded = content.count("Downloaded successfully")
            else:
                match = re.search(r"Number of downloads to process:\s*(\d+)", content)
                if match:
                    new_videos = match.group(1)
                    downloaded = content.count("Processing audio with duration")
                else:
                    match = re.search(r"New videos:\s*(\d+)", content)
                    if match:
                        new_videos = match.group(1)
                        downloaded = content.count("Downloaded successfully")
                    else:
                        new_videos = 0
                        downloaded = 0
            return new_videos, downloaded, "thành công", ""
        elif "Retrying" in content:
            match = re.search(r'attempt (\d+) of (\d+)', content)
            current_attempt = 0
            if match:
                current_attempt = int(match.group(1))  # 2
            return "", "", "đang thứ lại", current_attempt
        elif "Task is not able to be run" in content or "DAG failed" in content:
            return "", "", "thất bại", ""
        elif "Downloading" in content or "Processing" in content or "https://" in content:
            if "Starting batch download..." in content:
                downloaded = content.count("Downloaded successfully")
            else:
                match = re.search(r"Number of downloads to process:\s*(\d+)", content)
                if match:
                    downloaded = content.count("Processing audio with duration")
                else:
                    downloaded = 0
            return "", downloaded, "đang chạy", ""
        elif "Scrolling" in content:
                return "", "", "đang tìm video", ""
        else:
            return "", "", "chưa chạy", ""
        

def track_dag_status_ui(
    dag_id, dag_run_id, user_id,
    get_info_by_user_id, show_user_info_func,
    get_task_status_from_log_func,
    retry_task_func=retry_task  # Thêm tham số này
):

    st.title("Theo dõi trạng thái DAG và Task")
    status_placeholder = st.empty()
    retry_placeholder = st.empty()

    max_retries = 5
    try_number = 0
    wait_seconds = 300  # 5 phút

    airflow_api = AirflowAPI(
        base_url="http://airflow-webserver:8080",
        username="airflow",
        password="airflow"
    )

    def get_dag_state(dag_id,dag_run_id):
        dag_state = ''
        dag_status = airflow_api.get_dag_status(dag_id=dag_id, dag_run_id=dag_run_id)
        if dag_status:
            dag_state = str(dag_status['state'])
        return dag_state

    def logs_from_airflow_api(dag_id, dag_run_id, task_id):
        # Sử dụng
        task_status = None
        # if dag_status:
        try_number=1
        task_instances = airflow_api.get_task_instances(dag_id=dag_id, dag_run_id=dag_run_id)
        if task_instances and task_instances.get('task_instances'):
            for task_instance in task_instances['task_instances']:
                if task_instance.get('task_id') == task_id:
                    task_status = task_instance.get('state', 'Không tìm thấy trạng thái task')

                    try_number = int(task_instance.get('try_number', 1))
                    break  # Exit loop once we find the matching task

        if try_number <= 0:
            try_number =1

        return task_status, try_number

    _, get_links_try = logs_from_airflow_api(dag_id, dag_run_id, 'get_links_task')
    _, download_try = logs_from_airflow_api(dag_id, dag_run_id, 'batch_download_task')
    _, transcript_try = logs_from_airflow_api(dag_id, dag_run_id, 'audio_to_transcript_task')


    def get_status_list(get_links_try, download_try, transcript_try):

        get_links_log_file_path = f"/home/docon/projects/airflow-docker/logs/dag_id={dag_id}/run_id={dag_run_id}/task_id=get_links_task/attempt={get_links_try}.log"
        download_log_file_path = f"/home/docon/projects/airflow-docker/logs/dag_id={dag_id}/run_id={dag_run_id}/task_id=batch_download_task/attempt={download_try}.log"
        transcript_log_file_path = f"/home/docon/projects/airflow-docker/logs/dag_id={dag_id}/run_id={dag_run_id}/task_id=audio_to_transcript_task/attempt={transcript_try}.log"

        new_links, _, get_links_task_state, _ = get_task_status_from_log_func(get_links_log_file_path)
        _, downloaded_videos, download_task_state, _ = get_task_status_from_log_func(download_log_file_path)
        _, transcripted, transcript_task_state, _ = get_task_status_from_log_func(transcript_log_file_path)

        return [
            {'Task': 'Lấy link video', 'Trạng thái': f"{get_links_task_state}({new_links})", 'Lần chạy': get_links_try},
            {'Task': 'Download', 'Trạng thái': f"{download_task_state} ({downloaded_videos}/{new_links})", 'Lần chạy': download_try},
            {'Task': 'Chuyển đổi video thành transcript', 'Trạng thái': f"{transcript_task_state} ({transcripted}/{new_links})", 'Lần chạy':transcript_try}
        ], get_links_log_file_path

    dag_state = ""
    while not (dag_state=='success') and not (dag_state=='failed') :
        
        _, get_links_try = logs_from_airflow_api(dag_id, dag_run_id, 'get_links_task')
        _, download_try = logs_from_airflow_api(dag_id, dag_run_id, 'batch_download_task')
        _, transcript_try = logs_from_airflow_api(dag_id, dag_run_id, 'audio_to_transcript_task')

        task_status_list, get_links_log_file_path = get_status_list(get_links_try,download_try,transcript_try)
        status_placeholder.table(task_status_list)
        st.write('get_status_list:', get_links_log_file_path)
           
        dag_state = get_dag_state(dag_id, dag_run_id)
        
        time.sleep(5)


    task_status_list, _ = get_status_list(get_links_try,download_try,transcript_try)
    # task_status_list = logs_from_airflow_api(dag_id, dag_run_id)
    status_placeholder.table(task_status_list)
    if dag_state=='success':
        st.success("DAG đã hoàn thành!")
        if 'dag_run_id' in st.session_state:
            del st.session_state['dag_run_id']
        show_user_info_func(user_id)
    elif try_number >= max_retries:
        st.error("Đã retry tối đa 5 lần nhưng task vẫn chưa thành công.")