from src.exception import SrcException
from src.logger import logging
from src.predictor import ModelResolver
import pandas as pd
import numpy as np
from src.utils import load_object
import os,sys
from datetime import datetime
from src.config import ordinal_features , nominal_features , target_column
import warnings 
warnings.filterwarnings("ignore")

PREDICTION_DIR="prediction"


def start_batch_prediction(input_file_path):
    try:
        logging.info(f'{">"*20} Batch Prediction {"<"*20}')
        os.makedirs(PREDICTION_DIR,exist_ok=True)
        logging.info(f"Creating model resolver object")
        model_resolver = ModelResolver(model_registry="saved_models")
        logging.info(f"Reading file :{input_file_path}")
        df = pd.read_csv(input_file_path)
        df.replace({"na":np.NAN},inplace=True)
  
        logging.info(f"Loading transformer to transform dataset")
        
        #Lets load transformer pkl file
        transformer = load_object(file_path=model_resolver.get_latest_transformer_path()) 
        encoder=load_object(file_path=model_resolver.get_latest_encoder_path()) 

        
        #applying LableEncoder on Ordinal Features
        for feature_name in ordinal_features:
            df[feature_name]=encoder.transform(df[feature_name])

        input_feature_names =  list(transformer.feature_names_in_)  #all features tranformed while training model same as before
        feature_encoded_to_encoded = transformer.transform(df[input_feature_names]) #feature name  to be  tranformed 
        feature_encoded_df=pd.DataFrame(feature_encoded_to_encoded, columns=transformer.get_feature_names_out(input_feature_names)) #getting transformed features name
        #merging both tranformed  features and main df features
        df_encoded=pd.concat([df.drop(columns=input_feature_names).reset_index(drop=True), feature_encoded_df.reset_index(drop=True)], axis=1) 
        
        logging.info(f'{">"*20} Selecting Most Important Input Features  {"<"*20}')
        input_df=df_encoded.drop(target_column, axis=1) #new independent features after transformation 
        target_df=df_encoded[target_column] #In my case my Target is already Encoded 
        
        model = load_object(file_path=model_resolver.get_latest_model_path()) #loading best model
        prediction = model.predict(input_df)
        
        #applying LableEncoder on Ordinal Features
        for feature_name in ordinal_features:
            df[feature_name]=encoder.inverse_transform(df[feature_name])

        df["Prediction"] = prediction #adding new column for Prediction 
        prediction_file_name = os.path.basename(input_file_path).replace(".csv",f"{datetime.now().strftime('%m%d%Y__%H%M%S')}.csv")
        prediction_file_path = os.path.join(PREDICTION_DIR,prediction_file_name)
        df.to_csv(prediction_file_path,index=False,header=True)
        logging.info(f'{">"*20} Batch Prediction Completed Sucessfully {"<"*20}')
        return prediction_file_path
    
    except Exception as e:
        raise SrcException(e, sys)