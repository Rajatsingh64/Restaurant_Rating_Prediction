#!/bin/sh

# (Optional) Sync saved models from S3 if you need them.
# Remove or comment out if not required.
if [ -n "$BUCKET_NAME" ]; then
  echo "Syncing saved models from S3..."
  mkdir -p /app/saved_models
  aws s3 sync s3://$BUCKET_NAME/saved_models /app/saved_models
  echo "Saved models sync complete."
else
  echo "BUCKET_NAME is not set. Skipping saved models sync."
fi

# Wait a little to ensure Postgres is ready
sleep 30

# Initialize Airflow database
airflow db init

# Create an Airflow admin user if not already present
if ! airflow users list | grep -q "$AIRFLOW_USERNAME"; then
    airflow users create --email "$AIRFLOW_EMAIL" --firstname "Admin" --lastname "User" --password "$AIRFLOW_PASSWORD" --role "Admin" --username "$AIRFLOW_USERNAME"
fi

# Start Airflow webserver and scheduler in the background
airflow webserver -p 8080 &
airflow scheduler &

# Keep container running
exec tail -f /dev/null
