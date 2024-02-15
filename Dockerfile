FROM python:3.11-slim

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


WORKDIR /usr/src/app
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /usr/src/app

RUN apt-get purge -y --auto-remove gcc

# Workaround for permission issue on OpenShift
RUN chmod -R g+rw /usr/src/app

RUN chmod g+x /usr/src/app/docker-entrypoint.sh

ENV flag=1

EXPOSE 8000

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]

CMD ["sh", "-c", "gunicorn --bind=0.0.0.0:8000 --workers=${GUNICORN_WORKERS} --threads=${GUNICORN_THREADS} --access-logfile=- --log-file=- project.wsgi"]
