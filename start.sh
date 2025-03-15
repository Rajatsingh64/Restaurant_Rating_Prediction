#!/bin/sh

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
