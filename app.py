import streamlit as st
import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder
from src.utils import load_object, apply_label_encoder
from src.config import oridinal_features, nominal_features
from src.predictor import ModelResolver

# Streamlit page configuration
st.set_page_config(
    page_title="Zomato Rate Prediction 🍴",
    page_icon="🍴",
    layout="centered",
)

# Path to background image
background_image_path = "rest_image_free.jpg"  

# Display the background image using CSS
st.markdown(
    f"""
    <style>
        .stApp {{
            background-image: url("{background_image_path}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            height: 100vh;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Custom CSS for classy Zomato-like theme
st.markdown(
    """
    <style>
        body {
            background-color: #FFFFFF; /* White background */
        }
        .stApp {
            background-color: #FCECEC; /* Light reddish-white background */
        }
        h1, h2, h3, .stMarkdown {
            color: #E60012; /* Zomato Red for headers */
            font-family: Arial, sans-serif;
        }
        .stButton > button {
            background-color: #E60012; /* Zomato red button */
            color: white;
            font-size: 16px;
            font-weight: bold;
            border-radius: 5px;
            padding: 10px 15px;
            border: none;
        }
        .stButton > button:hover {
            background-color: #FF5733; /* Lighter red for hover */
            color: #FFFFFF;
        }
        .stTextInput, .stSelectbox, .stNumberInput, .stSlider {
            background-color: #FFFFFF; /* White input fields */
            color: black;
            border-radius: 5px;
            padding: 5px;
        }
        footer {
            font-size: 12px;
            text-align: center;
            margin-top: 30px;
            color: #E60012;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# App Title
st.title("Zomato Rate Prediction 🍴")

# Add Author Info
st.markdown(
    '<p style="text-align: center; font-size: 14px; color: #000000;">Created by <b>Rajat Singh</b> at <b>iNeuron.ai</b></p>',
    unsafe_allow_html=True,
)

# Load Model and Data
model_resolver = ModelResolver()
model_path = model_resolver.get_latest_model_path()
transformer_path = model_resolver.get_latest_transformer_path()
model = load_object(file_path=model_path)
transformer = load_object(file_path=transformer_path)

file_path = os.path.join(os.getcwd(), "dataset/cleaned_zomato.csv")
df = pd.read_csv(file_path)

# Inputs for the prediction
st.write("### Select Input Values for Prediction")
online_order = st.selectbox('Online Order (Yes/No)', ['Yes', 'No'])
book_table = st.selectbox('Book Table (Yes/No)', ['Yes', 'No'])
location = st.selectbox('Select Location', df['location'].unique())
rest_type = st.selectbox('Select Restaurant Type', df['rest_type'].unique())
cuisines = st.selectbox('Select Cuisines', df['cuisines'].unique())
approx_cost = st.number_input('Enter Approximate Cost', min_value=0.0, value=500.0)
votes = st.slider('Select Number of Votes', min_value=1, max_value=1000, value=100, step=1)

# Prepare input features for prediction
input_features = pd.DataFrame({
    'online_order': [online_order],
    'book_table': [book_table],
    'location': [location],
    'rest_type': [rest_type],
    'cuisines': [cuisines],
    'approx_cost': [approx_cost],
    'votes': [votes]
})

df = apply_label_encoder(df, oridinal_features)
encoded_features = transformer.transform(df[nominal_features])
encoded_df = pd.DataFrame(encoded_features, columns=transformer.get_feature_names_out())
input_df = pd.concat([df.drop(columns=nominal_features).reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)
input_df = input_df.drop("rate", axis=1)

# Prediction Button
if st.button('Predict Rate'):
    predicted_rate = model.predict(input_df)
    formatted_rate = round(predicted_rate[0], 1)  # Format to 1 decimal point
    st.write(f"### The Predicted Rate for the Selected Input is: **{formatted_rate} / 5**")

# Footer
st.markdown(
    '<footer>© 2025 Rajat Singh | iNeuron.ai | All Rights Reserved</footer>',
    unsafe_allow_html=True,
)
