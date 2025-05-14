import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

# === Cấu hình ===
AIRFLOW_URL = "http://192.168.247.40:8080"   # Thay bằng URL Airflow của bạn
DAG_ID = "pipeline_request"                       # Tên DAG muốn trigger
USERNAME = "airflow"                  # Tên đăng nhập Airflow
PASSWORD = "airflow"

# === Payload gửi đến API ===
payload = {
    "dag_run_id": f"manual__{datetime.now().isoformat()}",
    "conf": {
        "env": "prod",
        "run_type": "manual",
        "user_id": 123
    },
    "note": "Triggered from Python script",
    "logical_date": datetime.utcnow().isoformat() + "Z"
}

# === Gửi POST request ===
url = f"{AIRFLOW_URL}/api/v1/dags/{DAG_ID}/dagRuns"

response = requests.post(
    url,
    json=payload,
    auth=HTTPBasicAuth(USERNAME, PASSWORD),
    headers={"Content-Type": "application/json"}
)

# === In kết quả ===
if response.status_code in [200, 201]:
    print("✅ DAG triggered successfully!")
    print(response.json())
else:
    print("❌ Failed to trigger DAG.")
    print("Status code:", response.status_code)
    print("Response:", response.text)
