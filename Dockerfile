# ---- Final Application Image ----
FROM image-registry.openshift-image-registry.svc:5000/djamison-sandbox/base:latest

ENV APP_HOME=/opt/app-root/src
WORKDIR $APP_HOME

# Copy your Django project
COPY . $APP_HOME

# OpenShift requires group-writable directories
RUN mkdir -p $APP_HOME/staticfiles && \
    mkdir -p $APP_HOME/media && \
    chgrp -R 0 $APP_HOME && chmod -R g+rwX $APP_HOME

EXPOSE 8080

# Optional: bake static into the image
RUN python manage.py collectstatic --noinput || true

# Start Gunicorn
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8080"]
