# Use Python 3.12 as base image
FROM python:3.12-slim

USER root

# Create application directory and set working directory
RUN mkdir -p /app/airflow
WORKDIR /app

# Copy project files and DAGs
COPY . /app/
COPY ./dags /app/airflow/dags

# Upgrade pip
RUN pip3 install --upgrade pip

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install AWS CLI
RUN apt update -y && apt install -y awscli

# Set Airflow configuration environment variables
ENV AIRFLOW_HOME=/app/airflow
ENV AIRFLOW__CORE__DAGBAG_IMPORT_TIMEOUT=1000
ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True

# Make start.sh executable
RUN chmod +x start.sh

# Default command (can be overridden)
CMD ["sh", "-c", "echo 'Airflow container running. Use docker-compose commands.' && tail -f /dev/null"]
