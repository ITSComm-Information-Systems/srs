FROM base:latest

WORKDIR /usr/src/app

COPY . .

# Fix OpenShift permissions
RUN mkdir -p /usr/src/app/staticfiles
RUN chmod -R g+rw /usr/src/app/staticfiles
RUN chmod g+x /usr/src/app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]

CMD ["sh", "-c", "gunicorn --bind=0.0.0.0:8000 --workers=${GUNICORN_WORKERS} --threads=${GUNICORN_THREADS} --access-logfile=- --log-file=- project.wsgi"]
