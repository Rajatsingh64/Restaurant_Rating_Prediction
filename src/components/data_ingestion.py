from src.entity import config_entity , artifact_entity
from src.exception import SrcException
from src.logger import logging
from sklearn.model_selection import train_test_split
from src import utils
from src.config import mongo_client , featurs_to_drop
import pandas as pd
import os , sys

class DataIngestion:

    def __init__(self ,data_ingestion_config:config_entity.DataIngestionConfig):

        try:
            logging.info(f'{">"*20} DATA INGESTION {"<"*20}')
            self.data_ingestion_config=data_ingestion_config
        except Exception as e:
            raise SrcException(e ,sys)    
        

    def initiate_data_ingestion(self)-> artifact_entity.DataIngestionArtifact:

        try:
            logging.info(f'Exporting Data from MongoDB as pandas Dataframe')
            df= utils.get_collection_as_dataframe(database_name=self.data_ingestion_config.database_name ,
                                                  collection_name=self.data_ingestion_config.collection_name
                                                  )
            
            logging.info(f'Saving Data in feature store')
            #feature store directory path 
            feature_store_dir = os.path.dirname(self.data_ingestion_config.feature_store_file_path)
            
            #creating feature store folder if not available
            os.makedirs(feature_store_dir , exist_ok=True)
            logging.info(f'Save to feature Store Folder')

            df.to_csv(path_or_buf=self.data_ingestion_config.feature_store_file_path , index=False  , header=True)
            
            logging.info("split dataset into train and test set")
            #split dataset into train and test set
            train_df,test_df = train_test_split(df,test_size=self.data_ingestion_config.test_size,random_state=42)
            
            logging.info("create dataset directory folder if not available")
            #create dataset directory folder if not available
            dataset_dir = os.path.dirname(self.data_ingestion_config.train_file_path)
            os.makedirs(dataset_dir,exist_ok=True)

            logging.info("Save df to feature store folder")
            #Save df to feature store folder
            train_df.to_csv(path_or_buf=self.data_ingestion_config.train_file_path,index=False,header=True)
            test_df.to_csv(path_or_buf=self.data_ingestion_config.test_file_path,index=False,header=True)
            
            #Prepare artifact

            data_ingestion_artifact = artifact_entity.DataIngestionArtifact(
                feature_store_file_path=self.data_ingestion_config.feature_store_file_path,
                train_file_path=self.data_ingestion_config.train_file_path, 
                test_file_path=self.data_ingestion_config.test_file_path)

            logging.info(f"Data ingestion artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact

        except Exception as e:
            raise SrcException(e ,sys)
         


