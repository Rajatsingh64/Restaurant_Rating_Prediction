FROM python:3.8

# Declare build arguments for Airflow credentials
ARG AIRFLOW_EMAIL
ARG AIRFLOW_USERNAME
ARG AIRFLOW_PASSWORD

# Set environment variables from build arguments
ENV AIRFLOW_EMAIL=${AIRFLOW_EMAIL} \
    AIRFLOW_USERNAME=${AIRFLOW_USERNAME} \
    AIRFLOW_PASSWORD=${AIRFLOW_PASSWORD}

USER root
RUN mkdir -p /app
COPY . /app/
WORKDIR /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Set Airflow configuration environment variables
ENV AIRFLOW_HOME="/app/airflow" \
    AIRFLOW__CORE__DAGBAG_IMPORT_TIMEOUT=1000 \
    AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True \
    AIRFLOW__CORE__DAGS_FOLDER="/app/airflow/dags"

# Initialize the Airflow metadata database
RUN airflow db init

# (Optional) Check Airflow version
RUN airflow version

# Create an Airflow admin user
RUN airflow users create \
    --email "${AIRFLOW_EMAIL}" \
    --first "Rajat" \
    --last "Singh" \
    --password "${AIRFLOW_PASSWORD}" \
    --role "Admin" \
    --username "${AIRFLOW_USERNAME}"

# Allow script execution for start.sh (ensure your file uses Unix line endings)
RUN chmod +x start.sh

# Install AWS CLI (if needed)
RUN apt update -y && apt install -y awscli

# Set the default entrypoint and command (overridden by docker-compose)
ENTRYPOINT [ "/bin/sh" ]
CMD ["start.sh"]
