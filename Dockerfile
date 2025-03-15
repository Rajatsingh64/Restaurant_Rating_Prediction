# Use Python 3.12 as base image
FROM python:3.12

USER root

# Create application directory and copy files
RUN mkdir /app
COPY . /app/
WORKDIR /app/

# Update pip to the latest version
RUN pip3 install --upgrade pip

# Set environment variables for Airflow
ENV AIRFLOW_HOME="/app/airflow" \
    AIRFLOW__CORE__DAGBAG_IMPORT_TIMEOUT=1000 \
    AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True \
    AIRFLOW__CORE__DAGS_FOLDER="/app/airflow/dags"

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install AWS CLI for S3 operations
RUN apt update -y && apt install -y awscli

# Ensure start.sh is executable
RUN chmod +x start.sh

# Define a default command (to be overridden by docker-compose)
CMD ["sh", "-c", "echo 'Container started, override CMD in docker-compose' && exec tail -f /dev/null"]
