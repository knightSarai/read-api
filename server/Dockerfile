FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

WORKDIR /usr/src/app/

COPY requirements.txt ./

USER root

COPY . .


RUN pip install --no-cache-dir -r requirements.txt

