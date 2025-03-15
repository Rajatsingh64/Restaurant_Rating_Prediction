import os
import json
import subprocess
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.pipeline.batch_prediction_pipeline import start_batch_prediction

# Default DAG arguments
default_args = {
    'retries': 2,
}

# DAG definition
with DAG(
    'Restaurant_Rating_Prediction',
    default_args=default_args,
    description='Restaurant Rating Prediction',
    schedule_interval="@weekly",
    start_date=pendulum.datetime(2025, 3, 15, tz="UTC"),
    catchup=False,
    tags=['example'],
) as dag:

    def download_files(**kwargs):
        """
        Download input files from S3 to /app/input_files.
        """
        bucket_name = os.getenv("BUCKET_NAME")
        input_dir = "/app/input_files"
        os.makedirs(input_dir, exist_ok=True)  # Ensure directory exists
        os.system(f"aws s3 sync s3://{bucket_name}/input_files {input_dir}")
        print("Input files downloaded.")

    def batch_prediction(**kwargs):
        """
        Runs batch predictions for each file in /app/input_files.
        If model artifacts are missing, it syncs from S3 and retries.
        """
        input_dir = "/app/input_files"
        max_retries = 2

        for file_name in os.listdir(input_dir):
            file_path = os.path.join(input_dir, file_name)
            attempt = 0

            while attempt < max_retries:
                try:
                    start_batch_prediction(input_file_path=file_path)
                    print(f"Prediction completed for {file_name}.")
                    break  # Exit retry loop on success
                except FileNotFoundError as e:
                    attempt += 1
                    print(f"FileNotFoundError for {file_name}: {e}. Attempt {attempt} to sync models.")
                    
                    bucket_name = os.getenv("BUCKET_NAME")
                    if bucket_name:
                        sync_command = f"aws s3 sync s3://{bucket_name}/saved_models /app/saved_models"
                        try:
                            print("Syncing saved models from S3...")
                            subprocess.run(sync_command, shell=True, check=True)
                            print("Sync successful. Retrying prediction for", file_name)
                        except subprocess.CalledProcessError as sync_error:
                            print(f"Error syncing saved models: {sync_error}")
                            raise sync_error
                    else:
                        print("BUCKET_NAME is not set. Cannot sync models.")
                        raise e

                    if attempt >= max_retries:
                        print(f"Max retries reached for {file_name}.")
                        raise e
                except Exception as ex:
                    print(f"Unexpected error during prediction for {file_name}: {ex}")
                    raise ex

    def sync_predictions_to_s3(**kwargs):
        """
        Uploads local /app/prediction directory to S3.
        """
        bucket_name = os.getenv("BUCKET_NAME")
        os.system(f"aws s3 sync /app/prediction s3://{bucket_name}/prediction_files")
        print("Prediction files uploaded to S3.")

    # Define tasks
    download_task = PythonOperator(
        task_id="download_input_files",
        python_callable=download_files
    )

    prediction_task = PythonOperator(
        task_id="run_batch_prediction",
        python_callable=batch_prediction
    )

    upload_task = PythonOperator(
        task_id="upload_predictions",
        python_callable=sync_predictions_to_s3
    )

    # Define task dependencies
    download_task >> prediction_task >> upload_task
