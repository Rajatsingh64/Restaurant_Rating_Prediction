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
import time
import threading

warnings.filterwarnings("ignore")

# Streamlit page configuration
st.set_page_config(
    page_title="Zomato Rate Prediction 🍴",
    layout="centered",
)

# Paths to HTML and CSS templates
html_template_path = "templates/index.html"
css_template_path = "templates/style.css"

# Applying custom CSS
try:
    with open(css_template_path, "r") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.error("CSS file not found.")

try:
    with open(html_template_path, "r", encoding="utf-8") as html_file:
        st.markdown(html_file.read(), unsafe_allow_html=True)
except FileNotFoundError:
    st.error("HTML template file not found.")

# Flag to track training progress and thread reference for stopping
training_in_progress = False
training_thread = None
start_time = None
stop_training_event = threading.Event()

# Function to run the training pipeline
def run_training_pipeline():
    global training_in_progress, start_time
    try:
        training_in_progress = True
        start_time = time.time()  # Start time for training duration
        spinner_placeholder = st.empty()
        
        with spinner_placeholder.container():
            with st.spinner("Training pipeline is starting... Please wait."):

                # Start the training pipeline
                initiate_training_pipeline()
                
                # Simulate training steps (simplified for performance)
                for i in range(5):
                    if stop_training_event.is_set():
                        spinner_placeholder.text("Training has been stopped.")
                        return
                    time.sleep(2)
                    spinner_placeholder.text(f"Training in progress... Step {i + 1}/5")
                
                spinner_placeholder.success("Training complete. Model, transformer, and encoder saved.")
    except Exception as e:
        st.error(f"Error occurred: {e}")
    finally:
        training_in_progress = False

# Function to stop the training process
def stop_training():
    global stop_training_event
    stop_training_event.set()

# Button to trigger training or prediction
action = st.sidebar.radio("Select Action", ("Run Training Pipeline", "Predict Rate"))

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('cleaned_zomato.csv')

df = load_data()

# Load the latest model, transformer, and encoder
model_resolver = ModelResolver()
model_path = model_resolver.get_latest_model_path()
transformer_path = model_resolver.get_latest_transformer_path()
encoder_path = model_resolver.get_latest_encoder_path()

try:
    model = load_object(file_path=model_path)
    transformer = load_object(file_path=transformer_path)
    encoder = load_object(file_path=encoder_path)
except Exception as e:
    st.error(f"Error loading model, transformer, or encoder: {e}")

# Input feature selection for prediction
if action == "Predict Rate":
    st.write("### Select Input Values for Prediction")

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

    input_features = pd.DataFrame({
        "online_order": [online_order],
        "book_table": [book_table],
        "location": [location],
        "rest_type": [rest_type],
        "cuisines": [cuisines],
        "approx_cost": [approx_cost],
        "votes": [votes]
    })

    input_feature_names = list(transformer.feature_names_in_)

    try:
        feature_encoded_to_encoded = transformer.transform(input_features[input_feature_names])
        feature_encoded_df = pd.DataFrame(feature_encoded_to_encoded, columns=transformer.get_feature_names_out(input_feature_names))

        encoded_input_features = pd.concat([ 
            input_features.drop(columns=input_feature_names).reset_index(drop=True), 
            feature_encoded_df.reset_index(drop=True)
        ], axis=1)

        for col in ordinal_features:
            encoded_input_features[col] = encoder.transform(encoded_input_features[col])

    except Exception as e:
        st.error(f"Preprocessing error: {e}")
        encoded_input_features = None  # Ensure it doesn't proceed further if preprocessing fails

    # Only proceed to prediction if preprocessing was successful
    if encoded_input_features is not None:
        # Add a "Start Prediction" button for prediction
        if st.button("Start Prediction", key="start_prediction"):
            prediction_placeholder = st.empty()  # Create an empty container for the prediction result
            
            # Show a spinner during prediction
            with prediction_placeholder.container():
                with st.spinner("Making prediction... Please wait."):

                    time.sleep(2)  # Simulated delay to create prediction effect
                    try:
                        prediction_text = "The Predicted Rate for the Selected Input is: "
                        placeholder=st.empty()  # Placeholder to show animated output
                        # Prediction logic
                        predicted_rate = model.predict(encoded_input_features)
                        rate = round(predicted_rate[0], 1)
                        st.markdown(f'<p style="color: red; font-size: 24px; font-weight: bold; text-align: center;">{prediction_text}</p>', unsafe_allow_html=True)

                        for i in range(10):
                           # Only animate the predicted rate value, making it bigger with each transition
                           placeholder.markdown(f'<p style="color:red; font-size: {20+ i*5}px; text-align: center;">{round(rate, 1)} / 5</p>', unsafe_allow_html=True)
                           time.sleep(0.1)  # Delay between updates for animation
                        # Final prediction display with larger text after animation, centered and bold
                        placeholder.markdown(f'<p style="color: red; font-weight: bold; font-size: 50px; text-align: center;">{round(rate, 1)} / 5</p>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Prediction error: {e}")
            

# Start or stop training pipeline
if action == "Run Training Pipeline":
    if not training_in_progress:
        if st.button("Start Training"):
            # Reset stop event for a new training session
            stop_training_event.clear()
            # Start training in a separate thread
            training_thread = threading.Thread(target=run_training_pipeline, daemon=True)
            training_thread.start()
            
            # Real-time Timer Display
            timer_placeholder = st.empty()
            while training_in_progress:
                elapsed_time = round(time.time() - start_time, 1)
                timer_placeholder.markdown(f"**Training Time:** {elapsed_time}s")
                time.sleep(0.1)  # Update every 0.1 seconds

        st.button("Stop Training", on_click=stop_training)  # Stop button added

# Footer section
st.markdown(
    '<footer>© 2025 Rajat Singh | iNeuron.ai | All Rights Reserved</footer>',
    unsafe_allow_html=True,
)
