FROM python:3.12-slim

EXPOSE 8080

RUN apt-get update && apt-get install -y 
  

WORKDIR /app

COPY . /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt



ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]