FROM python:3.8-slim

ARG ENVIRONMENT="DEVELOPMENT"

ENV GUNICORN_WORKERS=2
ENV GUNICORN_THREADS=4

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get -y update && apt-get install -y libpq-dev gcc

#Oracle Instant Client
RUN apt-get install -y curl unzip libaio1 \
    && mkdir /opt/oracle && cd /opt/oracle \
    && curl --output instantclient.zip https://download.oracle.com/otn_software/linux/instantclient/19600/instantclient-basiclite-linux.x64-19.6.0.0.0dbru.zip \
    && unzip instantclient.zip && rm instantclient.zip
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_19_6

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

USER 1001
