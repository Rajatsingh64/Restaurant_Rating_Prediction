from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    feature_store_file_path:str
    train_file_path:str
    test_file_path:str


@dataclass
class DataValidationArtifact:
    report_file_path:str    


@dataclass
class DataTransformationArtifact:
    transformed_object_file_path:str   
    encoder_object_file_path:str 
    transformed_train_file_path:str
    transformed_test_file_path:str


@dataclass 
class ModelTrainerArtifact:
    model_file_path:str
    r2_train_score:str
    r2_test_score:str    


@dataclass
class ModelEvaluationArtifact:
    is_model_accepted:bool
    improved_accuracy:float   

@dataclass
class ModelPusherArtifact:
   pusher_model_dir:str
   saved_model_dir:str
   

@dataclass
class ModelPusherArtifact:
   pusher_model_dir:str
   saved_model_dir:str 