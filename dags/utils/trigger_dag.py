from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Cấu hình Airflow
AIRFLOW_API_URL = "http://192.168.247.40:8080/api/v2/dags"
AIRFLOW_USERNAME = "admin"
AIRFLOW_PASSWORD = "admin"  # hoặc dùng token

@app.route("/trigger-dag", methods=["POST"])
def trigger_dag():
    try:
        data = request.json
        dag_id = data.get("dag_id")
        conf = data.get("conf", {})

        if not dag_id:
            return jsonify({"error": "Missing dag_id"}), 400

        # Gửi POST request tới Airflow API
        response = requests.post(
            f"{AIRFLOW_API_URL}/{dag_id}/dagRuns",
            json={
                "conf": conf
            },
            auth=HTTPBasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200 or response.status_code == 201:
            return jsonify({"message": "DAG triggered successfully", "airflow_response": response.json()}), 200
        else:
            return jsonify({"error": "Failed to trigger DAG", "airflow_response": response.json()}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
