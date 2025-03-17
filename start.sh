#!/bin/sh
set -e

if [ "$1" = "airflow" ]; then
  echo "Starting S3 sync (if BUCKET_NAME is set)..."
  if [ -n "$BUCKET_NAME" ]; then
    mkdir -p /app/saved_models
    aws s3 sync s3://$BUCKET_NAME/saved_models /app/saved_models
    echo "Saved models sync complete."
  else
    echo "BUCKET_NAME is not set. Skipping S3 sync."
  fi

  echo "Migrating Airflow DB..."
  airflow db migrate

  echo "Checking if Admin user exists..."
  USER_EXISTS=$(airflow users list | grep "$AIRFLOW_USERNAME" || true)
  if [ -z "$USER_EXISTS" ]; then
    echo "Creating Admin user..."
    airflow users create \
      --email "$AIRFLOW_EMAIL" \
      --firstname "Admin" \
      --lastname "User" \
      --password "$AIRFLOW_PASSWORD" \
      --role "Admin" \
      --username "$AIRFLOW_USERNAME"
  else
    echo "Admin user exists."
  fi

  echo "Cleaning up any stale PID files..."
  rm -f /root/airflow-webserver.pid || true

  echo "Starting Supervisor for Airflow Scheduler & Webserver..."
  exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf

elif [ "$1" = "streamlit" ]; then
  echo "Starting Streamlit app..."
  exec streamlit run app.py --server.port 8501 --server.address=0.0.0.0 --server.enableCORS false
else
  echo "Unknown service: $1"
  exec "$@"
fi
