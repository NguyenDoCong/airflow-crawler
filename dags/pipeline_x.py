from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.get_transcript import audio_to_transcript
from tasks.x_videos_scraper import x_videos_scraper
from tasks.x_login import x_login
from tasks.batch_download import batch_download
from config import Config
from airflow.operators.python import PythonOperator
import math
from datetime import datetime

import sys
sys.path.append('/opt/airflow/dags')
# Define the DAG

# with DAG(
#     dag_id="x_login_dag",
#     schedule_interval=None,  # Set your desired schedule
#     start_date=days_ago(1),
#     catchup=False,
# ) as dag:
#     login = PythonOperator(
#         task_id="x_login_task",
#         python_callable=x_login,
#         provide_context=True,
#         op_kwargs={
#             "X_USERNAME": Config.X_USERNAME,
#             "X_PASSWORD": Config.X_PASSWORD,
#         },
#     )
    
#scraper    

def run_x_videos_scraper(**context):
    conf = context["dag_run"].conf or {}
    id = conf.get("id", "Cristiano")
    scrolls = math.ceil(conf.get("count", 20)/20)
    return x_videos_scraper(
        id=id,
        scrolls=scrolls,
    )

def login_x(**context):
    conf = context["dag_run"].conf or {}
    X_USERNAME = conf.get("X_USERNAME", Config.X_USERNAME)
    X_PASSWORD = conf.get("X_PASSWORD", Config.X_PASSWORD)
    return x_login(X_PASSWORD=X_PASSWORD,
                            X_USERNAME=X_USERNAME)

with DAG(
    dag_id="x_videos_scraper_dag",
    schedule="@daily",
    start_date=datetime.now(),
    catchup=False,
) as dag:
    
    login = PythonOperator(
        task_id="x_login_task",
        provide_context=True,
        python_callable=login_x,
    )

    urls = PythonOperator(
        task_id="get_links_task",
        provide_context=True,
        python_callable=run_x_videos_scraper,
    )

    downloads = PythonOperator(
        task_id="batch_download_task",
        python_callable=batch_download,
        provide_context=True,
        op_kwargs={"platform": "x"},
    )

    transcript = PythonOperator(
        task_id="audio_to_transcript_task",
        python_callable=audio_to_transcript,
        provide_context=True,
        op_kwargs={"platform": "x"},
    )

    login >> urls >> downloads >> transcript
