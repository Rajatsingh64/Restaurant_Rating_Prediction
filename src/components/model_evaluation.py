from src.entity import artifact_entity, config_entity
from src.exception import SrcException
from src.predictor import ModelResolver
from src.logger import logging
import os, sys
from src import utils
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
import streamlit as st
from src.config import target_column, ordinal_features, nominal_features


class ModelEvaluation:

    def __init__(self,
                 model_evaluation_config: config_entity.ModelEvaluationConfig,
                 data_ingestion_artifact: artifact_entity.DataIngestionArtifact,
                 data_transformation_artifact: artifact_entity.DataTransformationArtifact,
                 model_trainer_artifact: artifact_entity.ModelTrainerArtifact):
        try:
            logging.info(f'{">"*20} Model Evaluation {"<"*20}')
            self.model_evaluation_config = model_evaluation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_transformation_artifact = data_transformation_artifact
            self.model_trainer_artifact = model_trainer_artifact
            self.model_resolver = ModelResolver()
        except Exception as e:
            raise SrcException(e, sys)

    def _prepare_input(self, df: pd.DataFrame, encoder, transformer) -> pd.DataFrame:
        """
        Prepares the input DataFrame by:
        - Dropping target column
        - Encoding ordinal features using the provided encoder
        - Applying transformer (e.g., OneHotEncoder) to nominal features
        - Concatenating transformed features with non-encoded features
        """
        try:
            # Drop target column
            input_df = df.drop(target_column, axis=1).copy()

            # Encode ordinal features
            for col in ordinal_features:
                input_df[col] = encoder.transform(input_df[col])

            # Extract feature names used during transformation
            input_features_name = list(transformer.feature_names_in_)

            # Apply transformer on nominal features
            transformed = transformer.transform(input_df[input_features_name])
            transformed_df = pd.DataFrame(
                transformed,
                columns=transformer.get_feature_names_out(input_features_name)
            )

            # Combine transformed features with remaining features
            final_input_df = pd.concat(
                [
                    input_df.drop(columns=input_features_name).reset_index(drop=True),
                    transformed_df.reset_index(drop=True)
                ],
                axis=1
            ).reset_index(drop=True)

            return final_input_df
        except Exception as e:
            raise SrcException(e, sys)

    def initiate_model_evaluation(self) -> artifact_entity.ModelEvaluationArtifact:
        try:
            logging.info(f"Checking if a previously saved model exists for comparison")
            latest_dir_path = self.model_resolver.get_latest_dir_path()
            if latest_dir_path is None:
                model_evaluation_artifact = artifact_entity.ModelEvaluationArtifact(
                    is_model_accepted=True, improved_accuracy=None)
                logging.info(f"Model Evaluation artifact: {model_evaluation_artifact}")
                return model_evaluation_artifact

            logging.info(f"Fetching paths for previous Transformer, Model, and Encoder")
            transformer_path = self.model_resolver.get_latest_transformer_path()
            model_path = self.model_resolver.get_latest_model_path()
            encoder_path = self.model_resolver.get_latest_encoder_path()

            logging.info(f"Loading previously trained Transformer, Model, and Encoder")
            transformer = utils.load_object(file_path=transformer_path)
            model = utils.load_object(file_path=model_path)
            encoder = utils.load_object(file_path=encoder_path)

            logging.info(f"Loading currently trained Transformer, Model, and Encoder")
            current_model = utils.load_object(file_path=self.model_trainer_artifact.model_file_path)
            current_transformer = utils.load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            current_encoder = utils.load_object(file_path=self.data_transformation_artifact.encoder_object_file_path)

            # Load test data
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            target_df = test_df[target_column]

            # Evaluate previous model
            prev_input_df = self._prepare_input(test_df, encoder, transformer)
            prev_predictions = model.predict(prev_input_df)
            prev_r2_score = r2_score(target_df, prev_predictions)
            logging.info(f"R2 Score using previous model: {prev_r2_score}")

            # Evaluate current model
            current_input_df = self._prepare_input(test_df, current_encoder, current_transformer)
            current_predictions = current_model.predict(current_input_df)
            current_r2_score = r2_score(target_df, current_predictions)
            logging.info(f"R2 Score using current model: {current_r2_score}")

            if current_r2_score <= prev_r2_score:
                logging.info(f"Current trained model is not better than the previous model")
                raise Exception("Current trained model is not better than the previous model")

            model_eval_artifact = artifact_entity.ModelEvaluationArtifact(
                is_model_accepted=True,
                improved_accuracy=current_r2_score - prev_r2_score
            )
            logging.info(f"Model Evaluation Artifact: {model_eval_artifact}")
            return model_eval_artifact

        except Exception as e:
            raise SrcException(e, sys)
