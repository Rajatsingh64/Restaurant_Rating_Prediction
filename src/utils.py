import pandas as pd
import numpy as np 
from sklearn.preprocessing import LabelEncoder
from src.config import mongo_client
from src.exception import SrcException
import dill
import yaml
from src.logger import logging
import os,sys

def get_collection_as_dataframe(database_name , collection_name):
    """
    ===================================================================
    ThisFuntion is used to export Data from MongoDB and Convert it into Dataframe
    
    database_nameb :str = name of database inside MongoDB Atlas
    
    collection :str  = collection name inside MongoDB Atlas
    
    In case of error make sure to create .env file with mongo url 
    
    return dataframe as df
    ====================================================================
    """
    try:
        logging.info(f'collecting Data from Database {database_name} Collection {collection_name}')
        df=pd.DataFrame(mongo_client[database_name][collection_name].find())
        logging.info(f'Dataframe columns Available Rows {df.shape[0]} columns {df.shape[1]}')
        if '_id' in df.columns:
            df=df.drop("_id" , axis=1)
        return df 
    except Exception as e:
        print(e,sys)


def write_yaml_file(file_path,data:dict):
    try:
        file_dir = os.path.dirname(file_path)
        os.makedirs(file_dir,exist_ok=True)
        with open(file_path,"w") as file_writer:
            yaml.dump(data,file_writer)
    except Exception as e:
        raise SrcException(e, sys)
    

def convert_columns_float(df: pd.DataFrame, exclude_columns: list) -> pd.DataFrame:
    try:
        for column in df.columns:
            if column not in exclude_columns:
                if df[column].dtype == 'object':  # Check if it's a string
                    logging.info(f"Skipping conversion for non-numeric column: {column}")
                    continue  # Skip non-numeric columns

                try:
                    df[column] = df[column].astype('float')
                except ValueError as e:
                    logging.warning(f"Column '{column}' could not be converted to float: {e}")
        return df
    except Exception as e:
        raise e

    
def save_object(file_path:str , obj:object)->None:
    try:
        logging.info(f"Entered the Save_Object method of utils")
        os.makedirs(os.path.dirname(file_path) , exist_ok=True)
        with open(file_path , "wb") as file_obj:
            dill.dump(obj , file_obj)
        logging.info(f"Exited the Save Object of utils")  
    except Exception as e:
        raise SrcException(e,sys)      
    

def load_object(file_path:str , )-> object:
    try:
        if not os.path.exists(file_path):
            raise Exception(f" The file {file_path} not exists")
        with open(file_path , "rb") as file_obj:
            return dill.load(file_obj)
    except Exception as e:
        raise e   
    
def save_numpy_array_data(file_path:str , array:np.array):

    """  
    Save numpy array data to file
    file_path :str location of file to save
    array: np.array data to save
    """
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path , "wb") as file_obj:
            np.save(file_obj , array)
    except Exception as e:
        raise e        
    
def load_numpy_array_data(file_path:str) -> np.array:
    """
    load nump array data from file
    file_path :str location of file to load
    return: np.array data load
    """
    try:
        with open(file_path , "rb")as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise   SrcException(e,sys)   