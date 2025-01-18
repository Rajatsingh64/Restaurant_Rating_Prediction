import streamlit as st
import pandas as pd
import os
import sys
from src.utils import load_object, save_object, get_collection_as_dataframe
from src.config import ordinal_features, nominal_features
from src.pipeline.training_pipeline import initiate_training_pipeline
from src.predictor import ModelResolver
import warnings
from src.exception import SrcException
from src.logger import logging
import time  # For simulating delay (if needed for the animation effect)

warnings.filterwarnings("ignore")

# Streamlit page configuration to set the title, icon, and layout of the page
st.set_page_config(
    page_title="Zomato Rate Prediction 🍴",
    layout="centered",
)

# Path to templates for HTML and CSS
html_template_path = "templates/index.html"
css_template_path = "templates/style.css"

# Applying custom CSS to style the page
with open(css_template_path, "r") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


# Render HTML template for the app layout and structure
with open(html_template_path, "r", encoding="utf-8") as html_file:
    st.markdown(html_file.read(), unsafe_allow_html=True)


# Flag to track if the training is in progress
training_in_progress = False

# Run the Training Pipeline
def run_training_pipeline():
    global training_in_progress
    try:
        training_in_progress = True
        with st.spinner("Training pipeline is starting... Please wait."):
            # Call the training pipeline function
            initiate_training_pipeline()  # This starts the full pipeline
            
            # Simulating the steps (in actual usage, these steps are inside the pipeline)
            for i in range(10):
                time.sleep(2)
                st.text(f"Training in progress... Step {i + 1}/10")
            
            st.success("Training complete. Model, transformer, and encoder have been saved.")
        training_in_progress = False
    except Exception as e:
        st.error(f"Error occurred: {e}")
        training_in_progress = False

# Button to trigger training pipeline
if st.sidebar.button("Run Training Pipeline"):
    training_in_progress = False  # Reset flag to allow training to run
    with st.spinner("Training pipeline is starting... Please wait."):
        run_training_pipeline()

# Author's info in the footer of the page
st.markdown(
    '<p class="footer">Created by <b>Rajat Singh</b> at <b>iNeuron.ai</b></p>',
    unsafe_allow_html=True,
)

# Load data from the Zomato database collection and display a sample
df = get_collection_as_dataframe(database_name="Zomato", collection_name="Restaurant")

# Load the latest trained model, transformer, and encoder
model_resolver = ModelResolver()
model_path = model_resolver.get_latest_model_path()
transformer_path = model_resolver.get_latest_transformer_path()
encoder_path = model_resolver.get_latest_encoder_path()
model = load_object(file_path=model_path)
transformer = load_object(file_path=transformer_path)
encoder = load_object(file_path=encoder_path)

# Input feature selection for user prediction
st.write("### Select Input Values for Prediction")

# Create two columns for the inputs
col1, col2 = st.columns(2)

with col1:
    online_order = st.selectbox("Online Order", ["Yes", "No"], key="online_order")
    book_table = st.selectbox("Book Table", ["Yes", "No"], key="book_table")
    location = st.selectbox("Location", df["location"].unique(), key="location")
    rest_type = st.selectbox("Restaurant Type", df["rest_type"].unique(), key="rest_type")

with col2:
    cuisines = st.selectbox("Cuisines", df["cuisines"].unique(), key="cuisines")
    approx_cost = st.number_input("Approximate Cost", min_value=0.0, value=500.0, key="approx_cost")
    votes = st.slider("Number of Votes", min_value=1, max_value=1000, value=100, step=1, key="votes")

# Prepare the input for prediction based on user input
input_features = pd.DataFrame({
    "online_order": [online_order],
    "book_table": [book_table],
    "location": [location],
    "rest_type": [rest_type],
    "cuisines": [cuisines],
    "approx_cost": [approx_cost],
    "votes": [votes]
})

# Apply one-hot encoding on nominal features
input_feature_names = list(transformer.feature_names_in_)
feature_encoded_to_encoded = transformer.transform(input_features[input_feature_names])
feature_encoded_df = pd.DataFrame(feature_encoded_to_encoded, columns=transformer.get_feature_names_out(input_feature_names))

# Combine transformed features with other input features for final prediction
encoded_input_features = pd.concat([ 
    input_features.drop(columns=input_feature_names).reset_index(drop=True), 
    feature_encoded_df.reset_index(drop=True)
], axis=1)

# Apply label encoding on remaining categorical ordinal features
try:
    for col in ordinal_features:
        encoded_input_features[col] = encoder.transform(encoded_input_features[col])
except Exception as e:
    st.error(f"Error in processing input data: {e}")
    encoded_input_features = None

# Prediction button to make predictions based on the input features
prediction_text = "The Predicted Rate for the Selected Input is: "
if st.button("Predict Rate", disabled=training_in_progress):
    if encoded_input_features is not None:
        with st.spinner("Making prediction... Please wait."):

            time.sleep(2)  # Simulated delay to create prediction effect
            predicted_rate = model.predict(encoded_input_features)
            formatted_rate = round(predicted_rate[0], 1)  # Format to 1 decimal point

            # Disable the animated prediction message during training
            if not training_in_progress:
                # Static text for prediction description, making it bold
                st.markdown(f'<p style="color: red; font-size: 24px; font-weight: bold; text-align: center;">{prediction_text}</p>', unsafe_allow_html=True)

                # Placeholder to show animated prediction value
                placeholder = st.empty()  # Placeholder to show animated output
                for i in range(10):  # Simulated animation for smoother transition
                    rate = formatted_rate * (i + 1) / 10
                    # Only animate the predicted rate value, making it bigger with each transition
                    placeholder.markdown(f'<p style="color:red; font-size: {20+ i*5}px; text-align: center;">{round(rate, 1)} / 5</p>', unsafe_allow_html=True)
                    time.sleep(0.1)  # Delay between updates for animation

                # Final prediction display with larger text after animation, centered and bold
                placeholder.markdown(f'<p style="color: red; font-weight: bold; font-size: 50px; text-align: center;">{round(formatted_rate, 1)} / 5</p>', unsafe_allow_html=True)

    else:
        st.error("Prediction could not be made due to preprocessing error.")

# Footer section with copyright notice
st.markdown(
    '<footer>© 2025 Rajat Singh | iNeuron.ai | All Rights Reserved</footer>',
    unsafe_allow_html=True,
)
