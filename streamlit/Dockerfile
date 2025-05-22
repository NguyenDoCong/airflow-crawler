FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Expose the port the app runs on
EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--host", "0.0.0.0", "--port", "8501"]