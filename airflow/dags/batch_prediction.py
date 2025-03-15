import os
import subprocess
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'retries': 2,
}

with DAG(
    'Restaurant_Rating',
    default_args=default_args,
    description='Restaurant Rating Prediction',
    schedule_interval="@weekly",
    start_date=pendulum.datetime(2025, 3, 15, tz="UTC"),
    catchup=False,
    tags=['example'],
) as dag:

    def download_files(**kwargs):
        """
        Download input files from the S3 bucket to the local directory /app/input_files.
        """
        bucket_name = os.getenv("BUCKET_NAME")
        input_dir = "/app/input_files"
        # Create the directory if it doesn't exist
        os.makedirs(input_dir, exist_ok=True)
        command = f"aws s3 sync s3://{bucket_name}/input_files {input_dir}"
        os.system(command)
        print("Input files downloaded.")

    def batch_prediction(**kwargs):
        """
        For each file in /app/input_files, run the batch prediction pipeline.
        If the model or related artifacts are missing, sync the saved models from S3 and retry.
        """
        from src.pipeline.batch_prediction_pipeline import start_batch_prediction

        input_dir = "/app/input_files"
        for file_name in os.listdir(input_dir):
            file_path = os.path.join(input_dir, file_name)
            try:
                # Attempt prediction on the input file
                start_batch_prediction(input_file_path=file_path)
                print(f"Prediction completed for {file_name}.")
            except FileNotFoundError as e:
                print(f"FileNotFoundError for {file_name}: {e}. Attempting to sync saved models from S3.")
                bucket_name = os.getenv("BUCKET_NAME")
                if bucket_name:
                    sync_command = f"aws s3 sync s3://{bucket_name}/saved_models /app/saved_models"
                    try:
                        print("Syncing saved models from S3...")
                        subprocess.run(sync_command, shell=True, check=True)
                        print("Sync successful. Retrying prediction for", file_name)
                        start_batch_prediction(input_file_path=file_path)
                    except subprocess.CalledProcessError as sync_error:
                        print(f"Error syncing saved models: {sync_error}")
                        raise sync_error
                else:
                    print("BUCKET_NAME is not set. Cannot sync saved models.")
                    raise e
            except Exception as ex:
                print(f"An error occurred during prediction for {file_name}: {ex}")

    def sync_prediction_dir_to_s3_bucket(**kwargs):
        """
        Sync the local /app/prediction directory to the S3 bucket under prediction_files.
        """
        bucket_name = os.getenv("BUCKET_NAME")
        command = f"aws s3 sync /app/prediction s3://{bucket_name}/prediction_files"
        os.system(command)
        print("Prediction files synced to S3.")

    download_input_files = PythonOperator(
        task_id="download_input_files",
        python_callable=download_files,
    )

    generate_prediction_files = PythonOperator(
        task_id="generate_prediction_files",
        python_callable=batch_prediction,
    )

    upload_prediction_files = PythonOperator(
        task_id="upload_prediction_files",
        python_callable=sync_prediction_dir_to_s3_bucket,
    )

    download_input_files >> generate_prediction_files >> upload_prediction_files
