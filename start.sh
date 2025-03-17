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

# Migrate Airflow database
echo "Upgrading Airflow database..."
airflow db upgrade


echo "Ensuring Airflow Admin user exists..."
if ! airflow users list | grep -q "$AIRFLOW_USERNAME"; then
    airflow users create --email "$AIRFLOW_EMAIL" --firstname "Admin" --lastname "User" --password "$AIRFLOW_PASSWORD" --role "Admin" --username "$AIRFLOW_USERNAME"
    echo "Admin user created."
else
    echo "Admin user already exists."
fi

echo "Starting supervisord (webserver + scheduler)..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
