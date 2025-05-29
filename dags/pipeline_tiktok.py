from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.tiktok_videos_scraper import tiktok_videos_scraper
from tasks.batch_download import batch_download
from tasks.get_transcript import audio_to_transcript
from config import Config
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging

import sys
sys.path.append('/opt/airflow/dags')
# Define the DAG

# import signal
# from contextlib import contextmanager

# @contextmanager
# def timeout(seconds):
#     def timeout_handler(signum, frame):
#         raise TimeoutError(f"Function timed out after {seconds} seconds")
    
#     # Set the signal handler
#     signal.signal(signal.SIGALRM, timeout_handler)
#     signal.alarm(seconds)
    
#     try:
#         yield
#     finally:
#         # Reset the alarm
#         signal.alarm(0)

def run_tiktok_videos_scraper(**context):
    # with timeout(1000009):  # 85 giây, ít hơn execution_timeout
    conf = context["dag_run"].conf or {}
    id = conf.get("id", "hoaminzy_hoadambut")
    count = conf.get("count", 10)
    ms_tokens = conf.get("ms_tokens", Config.MS_TOKENS)
    download_directory = conf.get("download_directory", Config.DOWNLOAD_DIRECTORY)
    return tiktok_videos_scraper(
        id=id,
        count=count,
        ms_tokens=ms_tokens,
        DOWNLOAD_DIRECTORY=download_directory
    )

def log_retry(context):
    try_number = context['ti'].try_number
    max_tries = context['ti'].max_tries
    task_id = context['ti'].task_id
    logging.info(f"Retrying task {task_id}: attempt {try_number} of {max_tries + 1}")

with DAG(
    default_args={
        "depends_on_past": False,
        "retries": 5,
        "retry_delay": timedelta(seconds=10),
        'on_success_callback': lambda context: logging.info("DAG runs successfully"),
        'on_retry_callback': log_retry,
        'on_failure_callback': lambda context: logging.error("DAG failed"),
    },
    dag_id="tiktok_videos_scraper_dag",
    schedule="@daily",
    start_date=days_ago(0),
    catchup=False,
) as dag:

    urls = PythonOperator(
        task_id="get_links_task",
        provide_context=True,
        python_callable=run_tiktok_videos_scraper,
        # execution_timeout=timedelta(seconds=90)          
    )

    downloads = PythonOperator(
        task_id="batch_download_task",
        python_callable=batch_download,
        provide_context=True,
        op_kwargs={"platform": "tiktok"},
    )

    transcript = PythonOperator(
        task_id="audio_to_transcript_task",
        python_callable=audio_to_transcript,
        provide_context=True,
        op_kwargs={"platform": "tiktok"},
    )

    urls >> downloads >> transcript

# from airflow import DAG
# from airflow.utils.dates import days_ago
# from tasks.tiktok_videos_scraper import tiktok_videos_scraper
# from tasks.batch_download import batch_download
# from tasks.get_transcript import audio_to_transcript
# from config import Config
# from airflow.operators.python import PythonOperator
# from datetime import datetime, timedelta
# import logging
# import signal
# import sys
# import time

# sys.path.append('/opt/airflow/dags')

# # def timeout_handler(signum, frame):
# #     """Handler cho timeout signal"""
# #     logging.error(f"Task timeout after receiving signal {signum}")
# #     raise TimeoutError("Task execution timed out")

# def run_tiktok_videos_scraper(**context):
#     """Wrapper function với timeout handling tốt hơn"""
#     # Set up timeout handler
#     # signal.signal(signal.SIGALRM, timeout_handler)
#     # signal.alarm(80)  # Set timeout 80 giây (ít hơn execution_timeout)
    
#     try:
#         conf = context["dag_run"].conf or {}
#         id = conf.get("id", "realmadrid")
#         count = conf.get("count", 1)
#         ms_tokens = conf.get("ms_tokens", Config.MS_TOKENS)
#         download_directory = conf.get("download_directory", Config.DOWNLOAD_DIRECTORY)
        
#         logging.info(f"Starting scraping for ID: {id}, Count: {count}")
        
#         result = tiktok_videos_scraper(
#             id=id,
#             count=count,
#             ms_tokens=ms_tokens,
#             DOWNLOAD_DIRECTORY=download_directory
#         )
        
#         signal.alarm(0)  # Cancel alarm
#         logging.info(f"Scraping completed successfully: {result}")
#         return result
        
#     except TimeoutError:
#         logging.error("Task timed out - cleaning up...")
#         # Cleanup code here if needed
#         raise
#     except Exception as e:
#         signal.alarm(0)  # Cancel alarm
#         logging.error(f"Task failed with error: {str(e)}")
#         raise
#     finally:
#         signal.alarm(0)  # Ensure alarm is cancelled

# def safe_batch_download(**context):
#     """Wrapper cho batch download với timeout handling"""
#     try:
#         return batch_download(**context)
#     except Exception as e:
#         logging.error(f"Batch download failed: {str(e)}")
#         # Có thể retry hoặc skip tùy business logic
#         raise

# def safe_audio_to_transcript(**context):
#     """Wrapper cho transcript với timeout handling"""
#     try:
#         return audio_to_transcript(**context)
#     except Exception as e:
#         logging.error(f"Transcript failed: {str(e)}")
#         raise

# def log_retry(context):
#     try_number = context['ti'].try_number
#     max_tries = context['ti'].max_tries
#     task_id = context['ti'].task_id
#     dag_id = context['ti'].dag_id
#     execution_date = context['ti'].execution_date
    
#     logging.warning(
#         f"Retrying task {dag_id}.{task_id} "
#         f"(execution_date: {execution_date}): "
#         f"attempt {try_number} of {max_tries + 1}"
#     )

# def task_success(context):
#     task_id = context['ti'].task_id
#     dag_id = context['ti'].dag_id
#     execution_date = context['ti'].execution_date
    
#     logging.info(
#         f"Task {dag_id}.{task_id} "
#         f"(execution_date: {execution_date}) "
#         f"completed successfully"
#     )

# def task_failure(context):
#     task_id = context['ti'].task_id
#     dag_id = context['ti'].dag_id
#     execution_date = context['ti'].execution_date
#     exception = context.get('exception')
    
#     logging.error(
#         f"Task {dag_id}.{task_id} "
#         f"(execution_date: {execution_date}) "
#         f"failed with exception: {exception}"
#     )

# # DAG configuration
# default_args = {
#     "depends_on_past": False,
#     "retries": 5,  # Giảm số retry
#     "retry_delay": timedelta(minutes=5),  # Giảm retry delay
#     # "retry_exponential_backoff": True,  # Exponential backoff
#     # "max_retry_delay": timedelta(minutes=10),
#     'on_success_callback': task_success,
#     'on_retry_callback': log_retry,
#     'on_failure_callback': task_failure,
#     'task_timeout': timedelta(seconds=300)
# }

# with DAG(
#     default_args=default_args,
#     dag_id="tiktok_videos_scraper_dag",
#     description="Improved TikTok scraper with better timeout handling",
#     schedule="@daily",
#     start_date=days_ago(0),
#     catchup=False,
#     # max_active_runs=1,  # Chỉ cho phép 1 DAG run cùng lúc
#     # max_active_tasks=2,  # Giới hạn số task chạy đồng thời
# ) as dag:

#     # Task 1: Get video URLs
#     get_urls_task = PythonOperator(
#         task_id="get_links_task",
#         python_callable=run_tiktok_videos_scraper,
#         provide_context=True,
#         # execution_timeout=timedelta(minutes=5),  # Tăng timeout
#         # pool='scraper_pool',  # Sử dụng pool để giới hạn resource
#         # retry_delay=timedelta(minutes=1),
#         # task_timeout=timedelta(minutes=5)    
#     )

#     # Task 2: Download videos
#     download_task = PythonOperator(
#         task_id="batch_download_task",
#         python_callable=safe_batch_download,
#         provide_context=True,
#         op_kwargs={"platform": "tiktok"},
#         execution_timeout=timedelta(minutes=10),  # Timeout lớn hơn cho download
#         # pool='download_pool',
#     )

#     # Task 3: Generate transcripts
#     transcript_task = PythonOperator(
#         task_id="audio_to_transcript_task",
#         python_callable=safe_audio_to_transcript,
#         provide_context=True,
#         op_kwargs={"platform": "tiktok"},
#         execution_timeout=timedelta(minutes=15),  # Timeout lớn nhất cho transcript
#         # pool='transcript_pool',
#     )

#     # Define task dependencies
#     get_urls_task >> download_task >> transcript_task