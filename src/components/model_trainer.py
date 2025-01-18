from src.exception import SrcException
from src.logger import logging 
from src.utils import load_numpy_array_data , save_object
from src.entity import artifact_entity , config_entity 
from sklearn.ensemble import BaggingRegressor , RandomForestRegressor
from xgboost import XGBRFRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import RandomizedSearchCV
import warnings
import os , sys
warnings.filterwarnings("ignore")


class ModelTrainer:

    def __init__(self , model_trainer_config:config_entity.ModelTrainerConfig ,
                  data_transformation_artifact:artifact_entity.DataTransformationArtifact):
        
        try:
            logging.info(f"{'>'*20} Model Trainer {'>'*20}")
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact

        except Exception as e:
            raise SrcException(e , sys)    
        
    
    def model_tuning(self , model , X_train , y_train): #might take long time 
       
        try:
            logging.info(f"Model Tunning")
            # Define hyperparameter grid
            param_dist = {
                      "n_estimators": [50, 100, 200, 500],
                      "max_depth": [None, 10, 20, 30, 50],
                      "min_samples_split": [2, 5, 10],
                      "min_samples_leaf": [1, 2, 4],
                      "max_features": ["sqrt", "log2", None]}
            
            # Randomized Search
            random_search = RandomizedSearchCV(
                             estimator=model,
                             param_distributions=param_dist,
                             n_iter=20,  # Number of parameter settings to try
                             scoring='neg_mean_squared_error',  # Use appropriate metric
                             cv=3,  # Number of cross-validation folds
                             verbose=2,
                             random_state=42,
                             n_jobs=-1 ) # Use all processors
            # Train the model
            random_search.fit(X_train, y_train)

            # Get the best parameters and model
            best_model = random_search.best_estimator_

            return best_model
        
        except Exception as e:
            raise SrcException(e,sys)
    
    
    def initiate_model_training(self) -> artifact_entity.ModelTrainerArtifact:

        try:

            logging.info(f"Loading train and Test array file")
            train_array= load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_train_file_path)
            test_array= load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_test_file_path)

            logging.info(f"Spliting Target Feature from both train and test data")
            X_train , y_train =train_array[:,: -1] , train_array[:,-1]
            X_test , y_test=test_array[:,:-1] , test_array[:,-1]

            logging.info(f"Train the model")
            model=RandomForestRegressor(max_depth=300 ,random_state=42)
            model.fit(X_train ,y_train)
            
            #best model after Performing  hyper-parameter tuning 
            #model=self.model_tuning(model=model , X_train=X_train , y_train=y_train)
            logging.info(f"Calculating r2 train score")
            yhat_train=model.predict(X_train)
            r2_train_score=r2_score(y_train,yhat_train)
            
            logging.info(f"Calculating r2 test score")
            yhat_test =model.predict(X_test)
            r2_test_score=r2_score(y_test ,yhat_test)
            logging.info(f"train score: {r2_train_score} test score : {r2_test_score}")
            
            if r2_test_score < self.model_trainer_config.expected_score:
                raise Exception(f"Model is not good as it is not able to give \
                                expected accuracy :{self.model_trainer_config.expected_score}: Model actual score : {r2_test_score}")
            
            logging.info(f"checking if our model is overfitting or not")    
            diff =abs(r2_train_score - r2_test_score)

            if diff>self.model_trainer_config.overfitting_threshold:
                raise Exception(f"Train and Test Model Difference : {diff} is more than overfitting Threshold : {self.model_trainer_config.overfitting_threshold}")
            
            #save trained Model
            logging.info(f"Saving model Artifact")
            save_object(file_path=self.model_trainer_config.model_file_path , obj=model)

            #prepare artifact
            logging.info(f"Prepare artifact")
            model_trainer_artifact =artifact_entity.ModelTrainerArtifact(model_file_path=self.model_trainer_config.model_file_path ,
                                                                         r2_train_score=r2_train_score , r2_test_score=r2_test_score )
            logging.info(f"Model Trainer Artifact : {model_trainer_artifact}")
            return model_trainer_artifact
        
        except Exception as e:
            raise SrcException(e,sys)









