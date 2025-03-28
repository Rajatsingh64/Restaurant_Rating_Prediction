from asyncio import tasks
import json
from textwrap import dedent
import pendulum
import os
from airflow import DAG
from airflow.operators.python import PythonOperator


with DAG(
    'Restaurant_Rating_Model_Training',
    default_args={'retries': 1},
     max_active_runs=1,   # Only allow 1 active run at a time
     concurrency=4,       # Number of concurrent tasks allowed
    # [END default_args]
    description='Restaurant Rating Prediction',
    schedule_interval="@weekly",
    start_date=pendulum.datetime(2025, 3, 17, tz="UTC"),
    catchup=False,
    tags=['example'],
) as dag:

    
    def training(**kwargs):
        from src.pipeline.training_pipeline import initiate_training_pipeline
        initiate_training_pipeline()
    
    def sync_artifact_to_s3_bucket(**kwargs):
        bucket_name = os.getenv("BUCKET_NAME")
        os.system(f"aws s3 sync /app/artifact s3://{bucket_name}/artifacts")
        os.system(f"aws s3 sync /app/saved_models s3://{bucket_name}/saved_models")

    training_pipeline  = PythonOperator(
            task_id="train_pipeline",
            python_callable=training

    )

    sync_data_to_s3 = PythonOperator(
            task_id="sync_data_to_s3",
            python_callable=sync_artifact_to_s3_bucket

    )

    training_pipeline >> sync_data_to_s3