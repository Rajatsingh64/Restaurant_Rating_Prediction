# Use the official Python 3.12-slim image from Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file first to leverage Docker cache
COPY requirements.txt /app/

# Install dependencies
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Copy the rest of your application code into the container
COPY . /app/

# Expose port 8080 for the Streamlit app
EXPOSE 8080

# Set the entry point for the container to run the Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
