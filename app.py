import os
import time
import warnings
import subprocess  # Use subprocess for system calls
import streamlit as st
import pandas as pd
from src.utils import load_object
from src.config import ordinal_features
from src.predictor import ModelResolver
from dotenv import load_dotenv  # make sure python-dotenv is installed

warnings.filterwarnings("ignore")

# Load environment variables from .env (for local testing)
load_dotenv()

# Streamlit page configuration
st.set_page_config(
    page_title="Zomato Rate Prediction 🍴",
    layout="centered",
)

# Load CSS and HTML templates
def load_templates():
    try:
        with open("templates/style.css", "r") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CSS file not found.")
    try:
        with open("templates/index.html", "r", encoding="utf-8") as html_file:
            st.markdown(html_file.read(), unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("HTML template file not found.")

load_templates()

# Function to sync models from S3 using subprocess for better error handling
def sync_models():
    bucket_name = os.getenv("BUCKET_NAME")
    if not bucket_name:
        st.warning("BUCKET_NAME is not set. Cannot sync models.")
        return False

    st.info("Syncing latest model files from S3...")
    sync_command = ["aws", "s3", "sync", f"s3://{bucket_name}/saved_models", "/app/saved_models"]
    
    try:
        # subprocess.run returns a CompletedProcess object
        result = subprocess.run(sync_command, capture_output=True, text=True, check=True)
        st.success("Model files synced successfully.")
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to sync model files from S3. Error: {e.stderr}")
        return False

# Automatically sync models on startup
sync_models()

# Add a re-sync button in the sidebar
if st.sidebar.button("Re-sync Models"):
    sync_models()

# Load Data for Input Options
@st.cache_data
def load_data():
    return pd.read_csv('cleaned_zomato.csv')

df = load_data()

# Initialize ModelResolver using the local directory (adjust parameter name as needed)
model_resolver = ModelResolver(model_registry="/app/saved_models")
model_path = model_resolver.get_latest_model_path()
transformer_path = model_resolver.get_latest_transformer_path()
encoder_path = model_resolver.get_latest_encoder_path()

try:
    model = load_object(file_path=model_path)
    transformer = load_object(file_path=transformer_path)
    encoder = load_object(file_path=encoder_path)
except Exception as e:
    st.error(f"Error loading model, transformer, or encoder: {e}")

# Select Action: Prediction
action = st.sidebar.radio("Select Action", ("Predict Rate",), index=0)  # Default to 'Predict Rate'

if action == "Predict Rate":
    st.write("### Select Input Values for Prediction")

    # Layout columns for input widgets
    col1, col2 = st.columns(2)
    with col1:
        online_order = st.selectbox("Online Order", ["Yes", "No"], key="online_order")
        book_table = st.selectbox("Book Table", ["Yes", "No"], key="book_table")
        location = st.selectbox("Location", df["location"].unique(), key="location")
        rest_type = st.selectbox("Restaurant Type", df["rest_type"].unique(), key="rest_type")
    with col2:
        cuisines = st.selectbox("Cuisines", df["cuisines"].unique(), key="cuisines")
        approx_cost = st.number_input("Approximate Cost", min_value=0.0, value=500.0, key="approx_cost")
        votes = st.slider("Number of Votes", min_value=1, max_value=1500, value=100, step=1, key="votes")

    input_features = pd.DataFrame({
        "online_order": [online_order],
        "book_table": [book_table],
        "location": [location],
        "rest_type": [rest_type],
        "cuisines": [cuisines],
        "approx_cost": [approx_cost],
        "votes": [votes]
    })

    # Preprocessing and Encoding
    input_feature_names = list(transformer.feature_names_in_)
    try:
        feature_encoded = transformer.transform(input_features[input_feature_names])
        feature_encoded_df = pd.DataFrame(feature_encoded, columns=transformer.get_feature_names_out(input_feature_names))
        encoded_input_features = pd.concat([
            input_features.drop(columns=input_feature_names).reset_index(drop=True),
            feature_encoded_df.reset_index(drop=True)
        ], axis=1)
        # Apply encoding for ordinal features
        for col in ordinal_features:
            encoded_input_features[col] = encoder.transform(encoded_input_features[col])
    except Exception as e:
        st.error(f"Preprocessing error: {e}")
        encoded_input_features = None

    # Prediction Function
    def predict_rate(features):
        return model.predict(features)

    # Handle prediction if preprocessing was successful
    if encoded_input_features is not None:
        if st.button("Start Prediction", key="start_prediction"):
            with st.spinner("Making prediction... Please wait."):
                time.sleep(2)
                try:
                    prediction_text = "The Predicted Rate for the Selected Input is:"
                    st.markdown(
                        f'<p style="color: red; font-size: 24px; font-weight: bold; text-align: center;">{prediction_text}</p>',
                        unsafe_allow_html=True,
                    )
                    predicted_rate = predict_rate(encoded_input_features)
                    rate = round(predicted_rate[0], 1)

                    # Animated Transition for Rate Value
                    animation_placeholder = st.empty()
                    for size in range(20, 101, 5):
                        angle = (size - 20) * 3.6
                        animation_placeholder.markdown(
                            f"""
                            <div style="text-align: center; color: red;">
                                <span style="font-size: {size}px; transform: rotate({angle}deg); display: inline-block; font-weight: bold;">
                                    {rate}
                                </span>
                                <span style="font-size: 24px; font-weight: bold;"> / 5</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        time.sleep(0.05)
                    # Final Prediction Display
                    animation_placeholder.markdown(
                        f"""
                        <div style="text-align: center; color: red;">
                            <span style="font-size: 100px; font-weight: bold;">
                                {rate}
                            </span>
                            <span style="font-size: 24px; font-weight: bold;"> / 5</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                except Exception as e:
                    st.error(f"Prediction error: {e}")

# Footer Section
st.markdown(
    '<footer>© 2025 Rajat Singh | iNeuron.ai | All Rights Reserved</footer>',
    unsafe_allow_html=True,
)
