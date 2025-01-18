# Use the official Python 3.12 image from Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . /app/

# Expose the port the app will run on (Streamlit default is 8501)
EXPOSE 8501

# Command to run the app with Gunicorn and Streamlit
CMD ["gunicorn", "-b", "0.0.0.0:8501", "your_app:app"]
