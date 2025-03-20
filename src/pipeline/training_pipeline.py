from src.components.data_ingestion import DataIngestion
from src.components.data_validation import DataValidation
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer
from src.components.model_pusher import ModelPusher
from src.entity.config_entity import TrainingPipelineConfig , DataIngestionConfig , DataValidationConfig , DataTransformationConfig , ModelTrainerConfig
from src.entity.config_entity import ModelEvaluationConfig  , ModelPusherConfig
from src.components.model_evaluation import ModelEvaluation
from src.exception import SrcException
from src.logger import logging
import warnings 
warnings.filterwarnings("ignore")
import os,sys

def initiate_training_pipeline():

    try:
        #pipeline test
        training_pipeline_config = TrainingPipelineConfig()
        
        #Data Ingestion
        data_ingestion_config= DataIngestionConfig(training_pipeline_config=training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
        data_ingestion_artifact=data_ingestion.initiate_data_ingestion()
        print(f' {">"*20} Data Ingestion Pipeline Completed {"<"*20}')
        logging.info(f' {">"*20} Data Ingestion Pipeline Completed {"<"*20}')
        
        #Data Validation 
        data_validation_config=DataValidationConfig(training_pipeline_config=training_pipeline_config)
        data_validation=DataValidation(data_validation_config , data_ingestion_artifact)
        data_validation_artifact=data_validation.initiate_data_validation()
        print(f' {">"*20} Data Validation Pipeline Completed {"<"*20}')
        logging.info(f' {">"*20} Data Validation Pipeline Completed {"<"*20}')
        
        #Data Transformation 
        data_transformation_config=DataTransformationConfig(training_pipeline_config=training_pipeline_config)
        data_transfomation=DataTransformation(data_transformation_config , data_ingestion_artifact)
        data_transformation_artifact=data_transfomation.initiate_data_transformation()
        print(f' {">"*20} Data Transformation Pipeline Completed {"<"*20}')
        logging.info(f' {">"*20} Data Transformation Pipeline Completed {"<"*20}')
        
        #model Trainer
        model_trainer_config = ModelTrainerConfig(training_pipeline_config)
        model_trainer = ModelTrainer(model_trainer_config , data_transformation_artifact)
        model_trainer_artifact= model_trainer.initiate_model_training()
        print(f' {">"*20} Model Training Pipeline Completed {"<"*20}')
        logging.info(f' {">"*20} Model Training Pipeline Completed {"<"*20}')
        
        #model Evaluation 
        model_evaluation_config=ModelEvaluationConfig(training_pipeline_config)
        model_evaluation=ModelEvaluation(model_evaluation_config , data_ingestion_artifact , data_transformation_artifact , model_trainer_artifact)
        model_evaluation_artifact=model_evaluation.initiate_model_evaluation()
        print(f' {">"*20} Model Evaluation Pipeline Completed {"<"*20}')
        logging.info(f' {">"*20} Model Evaluation Pipeline Completed {"<"*20}')
      
        #Model Pusher 
        model_pusher_config=ModelPusherConfig(training_pipeline_config)
        model_pusher=ModelPusher(model_pusher_config , data_transformation_artifact , model_trainer_artifact)
        model_pusher_artifact=model_pusher.initiate_model_pusher()
        print(f' {">"*20} Model Pusher Pipeline Completed {"<"*20}')
        logging.info(f' {">"*20} Model Pusher Pipeline Completed {"<"*20}')
    
    except Exception as e:
        raise SrcException(e,sys)
        
