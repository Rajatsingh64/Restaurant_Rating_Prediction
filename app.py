import streamlit as st
import os, sys
from datetime import datetime
from src.exception import SrcException
from src.logger import logging
from src.predictor import ModelResolver
import pandas as pd
import numpy as np
from src.utils import load_object
from src.config import oridinal_features, nominal_features, target_column
from src.utils import apply_label_encoder

# Define the directory for storing predictions
PREDICTION_DIR = "prediction"

# Function to handle prediction
def start_single_prediction(input_data):
    try:
        logging.info(f'{">"*20} Single Prediction {"<"*20}')
        
        logging.info(f"Creating model resolver object")
        model_resolver = ModelResolver(model_registry="saved_models")
        
        # Apply transformations to input data
        input_data = apply_label_encoder(input_data, oridinal_features)

        # Load transformer pkl file
        transformer = load_object(file_path=model_resolver.get_latest_transformer_path())  
        input_feature_names = list(transformer.feature_names_in_)  # Features used in training
        feature_encoded = transformer.transform(input_data[input_feature_names])  # Transforming features
        feature_encoded_df = pd.DataFrame(feature_encoded, columns=transformer.get_feature_names_out(input_feature_names))  # Transformed feature names
        
        # Combine transformed features with original data
        input_data_encoded = pd.concat([input_data.drop(columns=input_feature_names).reset_index(drop=True), feature_encoded_df.reset_index(drop=True)], axis=1)
        
        logging.info(f'{">"*20} Selecting Input Features  {"<"*20}')
        input_df = input_data_encoded.drop('rate', axis=1, errors="ignore")  # Independent features
        
        # Load the best model
        model = load_object(file_path=model_resolver.get_latest_model_path())  
        
        # Perform prediction
        prediction = model.predict(input_df)
        
        return prediction[0]  # Return the predicted rate
    
    except Exception as e:
        raise SrcException(e, sys)

# Streamlit app for user input and prediction
st.title("Restaurant Rate Prediction App")

# Use a default CSV file or user input for prediction
file_path = os.path.join(os.getcwd(), "dataset/cleaned_zomato.csv")

if __name__ == "__main__":
    try:
        # Read the file and display the DataFrame for dropdowns
        df = pd.read_csv(file_path)
        
        # Dropdowns for selecting input data for prediction
        st.write("Select values for prediction:")

        # Add dropdowns for each of the features (for demonstration, we assume columns 'location', 'rest_type', 'cuisines')
        online_order = st.selectbox('Online Order (Yes/No)', ['Yes', 'No'])
        book_table = st.selectbox('Book Table (Yes/No)', ['Yes', 'No'])
        location = st.selectbox('Select Location', df['location'].unique())
        rest_type = st.selectbox('Select Restaurant Type', df['rest_type'].unique())
        cuisines = st.selectbox('Select Cuisines', df['cuisines'].unique())
        approx_cost = st.number_input('Enter Approximate Cost', min_value=0.0, value=500.0)
        
        # Add a slider for votes
        votes = st.slider('Select Number of Votes', min_value=1, max_value=1000, value=100, step=1)

        # Prepare the selected input data for prediction
        selected_input = pd.DataFrame({
            'online_order': [online_order],
            'book_table': [book_table],
            'location': [location],
            'rest_type': [rest_type],
            'cuisines': [cuisines],
            'approx_cost': [approx_cost],
            'votes': [votes]  # Add the votes slider value
        })

        # Button to trigger prediction
        if st.button('Predict'):
            st.write("Starting prediction...")

            # Trigger prediction with the selected input
            predicted_rate = start_single_prediction(selected_input)

            # Round the predicted rate to 1 decimal place
            predicted_rate_rounded = round(predicted_rate, 1)
            
            # Display the predicted rate
            st.success(f"The predicted rate for the selected input is: {predicted_rate_rounded}")
            
    except Exception as e:
        st.error(f"Error during prediction: {e}")
