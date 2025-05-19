import requests
from requests.auth import HTTPBasicAuth

def send_request():
    """
    Function to send a request to the Airflow API to trigger a DAG run.
    """
    # URL for the Airflow API endpoint
    # Replace with your Airflow instance URL if not running locally
    # Example: url = "http://your-airflow-instance:8080/api/v1/dags/tiktok_videos_scraper_dag/dagRuns"
    url = "http://localhost:8080/api/v1/dags/tiktok_videos_scraper_dag/dagRuns"
    payload = {
        "conf": {
            "id": "giadinhzozo",
            "count": 20
        }
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(
        url,
        json=payload,
        auth=HTTPBasicAuth("airflow", "airflow"),
        headers=headers
    )

    print("Status code:", response.status_code)
    print("Response:", response.text)

#main method
if __name__ == "__main__":
    send_request()