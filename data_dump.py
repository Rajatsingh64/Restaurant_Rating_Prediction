import pandas as pd
from src.config import mongo_client
import os ,sys

database_name = "Zomato"
collection_name="Restaurant"
file_path=os.path.join(os.getcwd() ,"dataset/cleaned_zomato.csv") #cleaned dataset inside researcj.ipynb file
##dataset link :-   https://www.kaggle.com/datasets/himanshupoddar/zomato-bangalore-restaurants

#creating  a funtion to dump dataset into mongodb database

if __name__=="__main__":
    
    df=pd.read_csv(file_path)
    #To dump data into Mongo db we need to convert data into keys and values format(eg.Dict or json format)
    data_dict=df.to_dict(orient="records")

    #dumping data into MongoDB database
    mongo_client[database_name][collection_name].insert_many(data_dict)
    print(f' Data Sucessfully Dumped inside MongoDB Atlas Database')

