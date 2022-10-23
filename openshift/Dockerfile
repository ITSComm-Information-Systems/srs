FROM python:3.9-slim

#ARG ENVIRONMENT="DEVELOPMENT"

RUN rm -r /usr/src/app
COPY . /usr/src/app

# Workaround for permission issue on OpenShift
RUN chmod -R g+rw /usr/src/app

RUN chmod g+x /usr/src/app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]

CMD ["sh", "-c", "gunicorn --bind=0.0.0.0:8000 --workers=${GUNICORN_WORKERS} --threads=${GUNICORN_THREADS} --access-logfile=- --log-file=- project.wsgi"]