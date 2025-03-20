from src.pipeline.training_pipeline import initiate_training_pipeline
from src.pipeline.batch_prediction_pipeline import start_batch_prediction
from src.exception import SrcException
from src.logger import logging
import os, sys

file_path=os.path.join(os.getcwd() ,"cleaned_zomato.csv")

if __name__=="__main__":
    try:
        training_ouput=initiate_training_pipeline()
        batch_output=start_batch_prediction(file_path)
        print(f'{">"*20} Current Prediction is {">"*20}')
        print(batch_output)


    except Exception as e:
        raise SrcException(e ,sys)