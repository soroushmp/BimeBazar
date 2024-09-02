FROM python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app/

RUN apt-get update
RUN apt-get upgrade -y

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

EXPOSE 8000