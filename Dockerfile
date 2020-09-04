FROM py38

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN set -x; \
        if [ "${ENVIRONMENT}" = "DEVELOPMENT" ]; then \
            pip install -r requirements.txt; \
        else \
            pip install -r requirements.prod.txt; \
        fi;

RUN apt-get purge -y --auto-remove gcc

# Workaround for permission issue on OpenShift
RUN chmod -R g+rw /usr/src/app

RUN chmod g+x /usr/src/app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]

CMD ["sh", "-c", "gunicorn --bind=0.0.0.0:8000 --workers=${GUNICORN_WORKERS} --threads=${GUNICORN_THREADS} --access-logfile=- --log-file=- rapid_time_entry.wsgi"]

