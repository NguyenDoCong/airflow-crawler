import requests
import base64
from datetime import datetime

class AirflowAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {self.auth}',
            'Content-Type': 'application/json'
        }
    
    def get_dag_status(self, dag_id,dag_run_id):
        """Lấy status của DAG"""
        # get dag run https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/get_dag_run
        url = f"{self.base_url}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    
    def get_task_instances(self, dag_id, dag_run_id):
        """Lấy task instances của một DAG run"""
        url = f"{self.base_url}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None
    
    def get_task_logs(self, dag_id, dag_run_id, task_id, try_number=1):
        """Lấy logs của task"""
        url = f"{self.base_url}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{try_number}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            try:
                return response.json()
            except Exception:
                return response.text  # Nếu không phải JSON, trả về text
        else:
            return None

