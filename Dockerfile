# Use official Python image
FROM python:3.12

# Declare build arguments
ARG AIRFLOW_EMAIL
ARG AIRFLOW_USERNAME
ARG AIRFLOW_PASSWORD

# Set environment variables from build arguments
ENV AIRFLOW_EMAIL=${AIRFLOW_EMAIL}
ENV AIRFLOW_USERNAME=${AIRFLOW_USERNAME}
ENV AIRFLOW_PASSWORD=${AIRFLOW_PASSWORD}

# Set Airflow-specific environment variables
ENV AIRFLOW_HOME="/app/airflow"
ENV AIRFLOW__CORE__DAGBAG_IMPORT_TIMEOUT=1000
ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True

# Set working directory
WORKDIR /app

# Copy all project files
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install AWS CLI
RUN apt update -y && apt install -y awscli supervisor

# Allow script execution
RUN chmod +x start.sh

# Initialize Airflow database
RUN airflow db init

# Create Airflow user
RUN airflow users create \
    --email "${AIRFLOW_EMAIL}" \
    --first "Rajat" \
    --last "Singh" \
    --password "${AIRFLOW_PASSWORD}" \
    --role "Admin" \
    --username "${AIRFLOW_USERNAME}" 

# Expose necessary ports (Airflow UI & Streamlit)
EXPOSE 8080 8501

# Copy supervisord configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set entrypoint to supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
