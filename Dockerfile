FROM python:3.12.9-slim
LABEL authors="honfi555"

WORKDIR /artHub-backend

COPY requirements.txt /artHub-backend/

COPY . /artHub-backend/
RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
