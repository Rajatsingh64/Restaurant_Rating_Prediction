from src.exception import SrcException
from src.logger import logging
import os , sys
from datetime import datetime


class TrainingPipelineConfig:

    def __init__(self):
        
        try:
            self.artifact_directory= os.path.join(os.getcwd() , "artifact" ,f"{datetime.now().strftime('%m%d%y__%H%M%S')}")

        except Exception as e:
            raise SrcException(e ,sys)    
        

class DataIngestionConfig:

    def __init__(self , training_pipeline_config:TrainingPipelineConfig):
        
        self.database_name="Zomato" #name of database 
        self.collection_name= "Restaurant" #Collection name
        self.data_ingestion_dir = os.path.join(training_pipeline_config.artifact_directory , "data_ingestion") 
        self.feature_store_file_path= os.path.join(self.data_ingestion_dir , "Feature_Store" , "ZOMATO.csv")
        self.train_file_path = os.path.join(self.data_ingestion_dir , "Datasets" , "train.csv")
        self.test_file_path = os.path.join(self.data_ingestion_dir , "Datasets" , "test.csv")
        self.test_size= 0.3 #Choose Threshold value provided by Domain Experts
          

class DataValidationConfig:
      
      def __init__(self , training_pipeline_config:TrainingPipelineConfig):
          
          self.data_validation_dir=os.path.join(training_pipeline_config.artifact_directory , "data_validation")
          self.report_file_path = os.path.join(self.data_validation_dir , "report.yml")
          self.missing_threshold=0.3 #random threshold
          self.base_data_file_path =os.path.join("cleaned_zomato.csv")  #Production dataset /old data for validation

class DataTransformationConfig:

    def __init__(self , training_pipeline_config:TrainingPipelineConfig):
          self.data_tranformer_dir=os.path.join(training_pipeline_config.artifact_directory , "data_transformer")
          self.transformed_object_file_path=os.path.join(self.data_tranformer_dir , "transformer.pkl")
          self.encoder_object_file_path=os.path.join(self.data_tranformer_dir , "encoder.pkl")
          self.data_tranformed_train_file_path= os.path.join(self.data_tranformer_dir , "transformed" , "train.npz")
          self.data_tranformed_test_file_path= os.path.join(self.data_tranformer_dir , "transformed" , "test.npz")
                             


class ModelTrainerConfig:

    def __init__(self,training_pipeline_config:TrainingPipelineConfig):

        self.model_trainer_dir=os.path.join(training_pipeline_config.artifact_directory , "model_trainer")
        self.model_file_path=os.path.join(self.model_trainer_dir ,"model" , "model.pkl")
        self.expected_score=0.8
        self.overfitting_threshold=0.1


class ModelEvaluationConfig:

    def __init__(self ,training_pipeline_config:TrainingPipelineConfig ):
             self.change_threshold = 0.1
    
class ModelPusherConfig:

    def __init__(self,training_pipeline_config:TrainingPipelineConfig):
        self.model_pusher_dir = os.path.join(training_pipeline_config.artifact_directory, "model_pusher")
        self.saved_model_dir = os.path.join("saved_models")
        self.pusher_model_dir = os.path.join(self.model_pusher_dir,"saved_models")
        self.pusher_model_path = os.path.join(self.pusher_model_dir,"model.pkl")
        self.pusher_transformer_path = os.path.join(self.pusher_model_dir,"transformer.pkl")
        self.pusher_encoder_path=os.path.join(self.pusher_model_dir , "encoder.pkl")