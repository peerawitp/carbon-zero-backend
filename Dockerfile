FROM python:3.9.17

WORKDIR /app

COPY . /app

RUN pip install -r ./app/requirements.txt