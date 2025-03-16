#!/bin/sh

# Sync saved models from S3 for prediction if BUCKET_NAME is set
if [ -n "$BUCKET_NAME" ]; then
  echo "Syncing saved models from S3..."
  mkdir -p /app/saved_models
  aws s3 sync s3://$BUCKET_NAME/saved_models /app/saved_models
  echo "Saved models sync complete. Listing contents:"
  ls -la /app/saved_models
else
  echo "BUCKET_NAME is not set. Skipping saved models sync."
fi

# Ensure the Airflow logs directory exists and set proper permissions
mkdir -p /opt/airflow/logs/scheduler
chown -R airflow:airflow /opt/airflow/logs

# Initialize Airflow database
airflow db init

# Wait for the database to be fully ready
sleep 10

# Create an Airflow admin user if not already present
if ! airflow users list | grep -q "$AIRFLOW_USERNAME"; then
    airflow users create --email "$AIRFLOW_EMAIL" --firstname "Rajat" --lastname "Singh" --password "$AIRFLOW_PASSWORD" --role "Admin" --username "$AIRFLOW_USERNAME"
fi

# Start Airflow webserver and scheduler in the background
airflow webserver -p 8080 &
airflow scheduler &

# Keep container running
exec tail -f /dev/null
