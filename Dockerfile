# Use Python 3.12 base image
FROM python:3.12-slim

# Set environment variables early
ENV AIRFLOW_HOME=/app/airflow
ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True
ENV AIRFLOW__CORE__DAGBAG_IMPORT_TIMEOUT=1000

# Set working directory
WORKDIR /app

# Copy everything into /app
COPY . /app/

# Install system dependencies & PostgreSQL driver, AWS CLI, Supervisor
RUN apt update -y && \
    apt install -y gcc libpq-dev awscli supervisor && \
    pip3 install --upgrade pip && \
    pip3 install psycopg2-binary && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Create logs directory
RUN mkdir -p /app/airflow/logs

# Copy Supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Make start script executable
RUN chmod +x start.sh

# Default command to start Airflow using Supervisor
CMD ["sh", "./start.sh"]
