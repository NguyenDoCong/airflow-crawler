import streamlit as st
import pandas as pd
import os
import re
import time

def show_user_info(user_id, platform, get_info_by_user_id):
    user_detail = get_info_by_user_id(user_id, platform=platform)
    st.markdown("---")
    infos = pd.DataFrame(columns=["video_id", "transcript"])
    for item in user_detail:
        display_info = {
            "video_id": item.video_id,
            "transcript": item.transcript}
        infos = pd.concat([infos, pd.DataFrame([display_info])], ignore_index=True)
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
    if not os.path.exists(log_file_path):
        return "", "", "chưa chạy"
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
            return new_videos, downloaded, "thành công"
        elif "Retrying" in content:
            return "", "", "đang thứ lại"
        elif "Task is not able to be run" in content or "DAG failed" in content:
            return "", "", "thất bại"
        elif "Downloading" in content or "Processing" in content or "https://" in content:
            if "Starting batch download..." in content:
                downloaded = content.count("Downloaded successfully")
            else:
                match = re.search(r"Number of downloads to process:\s*(\d+)", content)
                if match:
                    downloaded = content.count("Processing audio with duration")
                else:
                    downloaded = 0
            return "", downloaded, "đang chạy"
        elif "Scrolling" in content:
                return "", "", "đang tìm video"
        else:
            return "", "", "chưa chạy"

def track_dag_status_ui(dag_id, dag_run_id, user_id, get_info_by_user_id, show_user_info_func, stop_dag_func, get_task_status_from_log_func):
    import time
    import streamlit as st

    st.title("Theo dõi trạng thái DAG và Task")
    status_placeholder = st.empty()
    # start_time = time.time()
    # timeout = 90

    def get_status_list():
        get_links_log_file_path = f"/home/docon/projects/airflow-docker/logs/dag_id={dag_id}/run_id={dag_run_id}/task_id=get_links_task/attempt=1.log"
        download_log_file_path = f"/home/docon/projects/airflow-docker/logs/dag_id={dag_id}/run_id={dag_run_id}/task_id=batch_download_task/attempt=1.log"
        transcript_log_file_path = f"/home/docon/projects/airflow-docker/logs/dag_id={dag_id}/run_id={dag_run_id}/task_id=audio_to_transcript_task/attempt=1.log"
        new_links, _, get_links_task_state = get_task_status_from_log_func(get_links_log_file_path)
        _, downloaded_videos, download_task_state = get_task_status_from_log_func(download_log_file_path)
        _, transcripted, transcript_task_state = get_task_status_from_log_func(transcript_log_file_path)
        return [
            {'Task': 'Lấy link video', 'Trạng thái': f"{get_links_task_state}({new_links})"},
            {'Task': 'Download', 'Trạng thái': f"{download_task_state} ({downloaded_videos}/{new_links})"},
            {'Task': 'Chuyển đổi video thành transcript', 'Trạng thái': f"{transcript_task_state} ({transcripted}/{new_links})"}
        ]

    def check_task_status():
        status = get_status_list()
        return all("thành công" in task["Trạng thái"] for task in status)

    while not check_task_status():
        task_status_list = get_status_list()
        status_placeholder.table(task_status_list)
        # if task_status_list[0]["Trạng thái"] == "chưa chạy()":
        #     elapsed = time.time() - start_time
        #     if elapsed > timeout:
        #         stop_dag_result, stop_dag_message = stop_dag_func(dag_id, dag_run_id)
        #         if stop_dag_result:
        #             st.success(stop_dag_message)
        #         else:
        #             st.error(stop_dag_message)
        #         st.error("Task chưa chạy sau 1 phút. Đã gửi yêu cầu dừng DAG.")
        #         break
        # else:
        #     start_time = time.time()
        time.sleep(1)

    task_status_list = get_status_list()
    status_placeholder.table(task_status_list)
    if check_task_status():
        st.success("DAG đã hoàn thành!")
        del st.session_state['dag_run_id']
        show_user_info_func(user_id)

    # if st.button("Close"):
    #     st.rerun()