FROM python:3.11-slim

ENV GUNICORN_WORKERS=2
ENV GUNICORN_THREADS=4

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get -y update && apt-get install -y gcc

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
