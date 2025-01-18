from src.entity import config_entity , artifact_entity
from src.exception import SrcException
from src.entity.config_entity import DataValidationConfig 
from src.entity.artifact_entity import DataIngestionArtifact , DataTransformationArtifact
from src.logger import logging
from scipy.stats import ks_2samp, chi2_contingency
from typing import Optional
from src.config import target_column , ordinal_features , nominal_features
from sklearn.preprocessing import OneHotEncoder , LabelEncoder
from src.utils import load_numpy_array_data , save_object , load_object , save_numpy_array_data 
import numpy as np
import dill
import re
import pandas as pd
from src import utils
import pandas as pd
import os , sys


class DataTransformation:

    def __init__(self , data_transformation_config:config_entity.DataTransformationConfig ,
                 data_ingestion_artifact:DataIngestionArtifact ,):
        try:
            logging.info(f'{">"*20} Data Transformation {"<"*20}')
            self.data_transformation_config=data_transformation_config
            self.data_ingestion_artifact=data_ingestion_artifact
        except Exception as e:
            raise SrcException(e ,sys)     
        

    def initiate_data_transformation(self)->DataTransformationArtifact:
        
        try:
            logging.info(f'Reading Train and Test data as DataFrame')
            #reading data as pd.dataframe
            train_df= pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df= pd.read_csv(self.data_ingestion_artifact.test_file_path)
            
            #applying lable encoding to ordinal features
            encoder=LabelEncoder() 
            
            for col in ordinal_features:
                 train_df[col]=encoder.fit_transform(train_df[col])
                 test_df[col]=encoder.transform(test_df[col])
            
            one_hot_encoder= OneHotEncoder(sparse_output=False ,handle_unknown="ignore")
            #Lets apply One_Hot_Encoder on train_df 
            logging.info(f' Applying OneHotEncoding to this Nominal Features inside training data {nominal_features}')
            encoded_train_df  = one_hot_encoder.fit_transform(train_df[nominal_features])
            train_encoded_df = pd.DataFrame(encoded_train_df, columns=one_hot_encoder.get_feature_names_out())
            
            # Transform on test data
            test_encoded_features = one_hot_encoder.transform(test_df[nominal_features])
            test_encoded_df = pd.DataFrame(test_encoded_features, columns=one_hot_encoder.get_feature_names_out())
            
            logging.info(f"Data tranformed for this features :{nominal_features}")

            # Concatenate the original DataFrame (without the nominal features) with the new encoded DataFrame
            train_df = pd.concat([train_df, train_encoded_df], axis=1)
            train_df=train_df.drop(nominal_features , axis=1)
            
            #test encoded feature
            test_df = pd.concat([test_df , test_encoded_df], axis=1)
            test_df=test_df.drop(nominal_features , axis=1)
            
           
            logging.info(f"Spliting inpur features for both Train and Test data")
            #Select Input Features for both train and test data
            input_features_train_df= train_df.drop(target_column , axis=1)
            input_features_test_df=test_df.drop(target_column , axis=1)

            #selecting target features from both train and test dataframe
            target_feature_train_df= train_df[target_column]
            target_feature_test_df= test_df[target_column]

            logging.info(f"spliting target features for train and test data")
           
            #target encoder
            train_arr = np.c_[input_features_train_df,target_feature_train_df]
            test_arr=np.c_[input_features_test_df,target_feature_test_df]
            
            #save numpy array 
            save_numpy_array_data(file_path=self.data_transformation_config.data_tranformed_train_file_path, array=train_arr)
            save_numpy_array_data(file_path=self.data_transformation_config.data_tranformed_test_file_path , array=test_arr)
            
            #input feature  encoder object
            save_object(self.data_transformation_config.transformed_object_file_path , obj=one_hot_encoder)
            save_object(self.data_transformation_config.encoder_object_file_path , obj=encoder)


            data_tranformation_artifact=DataTransformationArtifact(
                                   transformed_object_file_path = self.data_transformation_config.transformed_object_file_path,
                                   encoder_object_file_path=self.data_transformation_config.encoder_object_file_path,
                                   transformed_train_file_path =self.data_transformation_config.data_tranformed_train_file_path,
                                   transformed_test_file_path =self.data_transformation_config.data_tranformed_test_file_path
            )
            logging.info(f"Data Transformation Object {data_tranformation_artifact}")
            return data_tranformation_artifact
        
        except Exception as e:
            raise SrcException(e,sys)    