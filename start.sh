#!/bin/sh

# (Optional) Sync saved models from S3 if needed.
if [ -n "$BUCKET_NAME" ]; then
  echo "Syncing saved models from S3..."
  mkdir -p /app/saved_models
  aws s3 sync s3://$BUCKET_NAME/saved_models /app/saved_models
  echo "Saved models sync complete."
else
  echo "BUCKET_NAME is not set. Skipping saved models sync."
fi

# Wait to ensure Postgres is ready
sleep 30

# Initialize Airflow DB
airflow db upgrade

# Create Airflow admin user (idempotent)
if ! airflow users list | grep -q "$AIRFLOW_USERNAME"; then
  airflow users create \
    --email "$AIRFLOW_EMAIL" \
    --firstname "Admin" --lastname "User" \
    --password "$AIRFLOW_PASSWORD" \
    --role "Admin" \
    --username "$AIRFLOW_USERNAME"
fi

# Start webserver on port 8080
airflow webserver -p 8080
