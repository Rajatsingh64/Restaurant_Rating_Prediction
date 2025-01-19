# Use the official Python 3.12 image from Docker Hub
FROM python:3.12-slim

# Set environment variables to avoid writing .pyc files to the container
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Create a non-root user and set as the default user
RUN useradd -m appuser
USER appuser

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY --chown=appuser:appuser requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY --chown=appuser:appuser . /app/

# Expose the port the app will run on (Streamlit default is 8501, but using 8080 in this case)
EXPOSE 8080

# Command to run the Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
