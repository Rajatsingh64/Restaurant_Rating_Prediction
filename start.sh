#!/bin/sh
set -e

echo "Starting S3 sync (if BUCKET_NAME is set)..."
if [ -n "$BUCKET_NAME" ]; then
  mkdir -p /app/saved_models
  aws s3 sync s3://$BUCKET_NAME/saved_models /app/saved_models
  echo "Saved models sync complete."
else
  echo "BUCKET_NAME is not set. Skipping S3 sync."
fi

echo "Migrating Airflow DB..."
airflow db upgrade

echo "Checking if Admin user exists..."
USER_EXISTS=$(airflow users list | grep "$AIRFLOW_USERNAME" || true)

if [ -z "$USER_EXISTS" ]; then
  echo "Admin user does not exist. Creating fresh Admin user..."
  airflow users create \
    --email "$AIRFLOW_EMAIL" \
    --firstname "Admin" \
    --lastname "User" \
    --password "$AIRFLOW_PASSWORD" \
    --role "Admin" \
    --username "$AIRFLOW_USERNAME"
else
  echo "Admin user already exists. Skipping creation."
fi

echo "Starting Supervisor to run Scheduler and Webserver..."
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
