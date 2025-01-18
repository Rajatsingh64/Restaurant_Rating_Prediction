from dotenv import load_dotenv
from dataclasses import dataclass
import os ,sys
import pymongo as pm

print(f' Loading .env')
load_dotenv()

#creating class for Environment Variables
@dataclass
class EnvironmentVariables:
    mongo_url:str=os.getenv("MONGO_DB_URL")

env=EnvironmentVariables()

mongo_client=pm.MongoClient(env.mongo_url)
print(f'Connected to MongoDB Database')

target_column= "rate" #dependent feature
featurs_to_drop=['url', 'name' ,'address','phone' ,'listed_in(type)' ,'reviews_list' , "menu_item" , 'dish_liked' , 'listed_in(city)'] #irrevalent features
nominal_features = ["location", "cuisines","rest_type"]
ordinal_features = [ "online_order" , "book_table"]