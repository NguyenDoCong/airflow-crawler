# Base image
FROM apache/airflow:2.10.0-python3.10

# Switch to root for system dependencies
USER root

# Install system dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    ffmpeg \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt update && apt install -y iputils-ping

# Set Chrome options for running in container
ENV CHROME_BIN=/usr/bin/chromium
# ENV CHROME_DRIVER=/usr/bin/chromedriver
ENV DISPLAY=:99

# Copy requirements and set permissions
COPY --chown=airflow:root requirements.txt /opt/airflow/requirements.txt

# Switch to airflow user for pip installations
USER airflow

# Install Python dependencies
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt \
    && pip install --no-cache-dir playwright>=1.52
    
# RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Switch back to root for system configurations
USER root

# Setup Playwright and Chrome directories
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/airflow/.cache/ms-playwright
RUN mkdir -p ${PLAYWRIGHT_BROWSERS_PATH} \
    && mkdir -p /opt/airflow/.config/chromium \
    && playwright install chromium --with-deps \
    && chown -R airflow:root ${PLAYWRIGHT_BROWSERS_PATH} /opt/airflow/.config \
    && chmod -R 775 ${PLAYWRIGHT_BROWSERS_PATH} /opt/airflow/.config

# Create and set permissions for Airflow directories
RUN mkdir -p /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins /opt/airflow/data \
    && chown -R airflow:root /opt/airflow \
    && chmod -R 775 /opt/airflow

# Set working directory
WORKDIR /opt/airflow

# Set Python path
ENV PYTHONPATH=/opt/airflow

# Switch back to airflow user for security
USER airflow


# Expose ports (if needed)
EXPOSE 8080