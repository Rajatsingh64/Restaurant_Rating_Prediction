FROM python:3.12-slim

ENV AIRFLOW_HOME=/app/airflow
ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True
ENV AIRFLOW__CORE__DAGBAG_IMPORT_TIMEOUT=1000

WORKDIR /app

COPY . /app/

RUN apt update -y && \
    apt install -y gcc libpq-dev awscli supervisor && \
    pip3 install --upgrade pip && \
    pip3 install psycopg2-binary && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/airflow/logs
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN chmod +x start.sh

ENTRYPOINT ["sh", "./start.sh"]
