FROM python:3.12.9-slim
LABEL authors="honfi555"

WORKDIR /artHub-backend

COPY requirements.txt /artHub-backend/

COPY . /artHub-backend/
RUN pip3 install -r requirements.txt

EXPOSE 8080

RUN ["uvicorn", "app.main:app", "--port", "8080"]