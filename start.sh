#!/bin/sh

# Sync saved models from S3 if BUCKET_NAME is set
if [ -n "$BUCKET_NAME" ]; then
  echo "Syncing saved models from S3..."
  mkdir -p /app/saved_models
  aws s3 sync s3://$BUCKET_NAME/saved_models /app/saved_models
  echo "Saved models sync complete."
else
  echo "BUCKET_NAME is not set. Skipping saved models sync."
fi

# Initialize Airflow database
airflow db init

# Create Airflow admin user if not exists
if ! airflow users list | grep -q "$AIRFLOW_USERNAME"; then
    airflow users create --email "$AIRFLOW_EMAIL" --firstname "Admin" --lastname "User" --password "$AIRFLOW_PASSWORD" --role "Admin" --username "$AIRFLOW_USERNAME"
fi

# Start supervisord (which handles webserver + scheduler)
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
