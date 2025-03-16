# Use Python 3.12 base image
FROM python:3.12

USER root

# Create and set working directory
RUN mkdir /app
WORKDIR /app
COPY . /app/

# Update pip to latest version
RUN pip3 install --upgrade pip

# Install Postgres driver, AWS CLI, Supervisor
RUN apt update -y && \
    apt install -y awscli supervisor && \
    pip3 install psycopg2-binary

# Airflow configurations
ENV AIRFLOW_HOME=/app/airflow
ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True
ENV AIRFLOW__CORE__DAGBAG_IMPORT_TIMEOUT=1000

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Create Airflow logs directory
RUN mkdir -p /app/airflow/logs

# Copy Supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Make start script executable
RUN chmod +x start.sh

# Default command to start Airflow using Supervisor
CMD ["sh", "./start.sh"]
