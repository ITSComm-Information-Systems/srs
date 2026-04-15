# This will build the base image to be used for the s2i environment builds.
# First line will be replaced with the image in the openshift build.
FROM registry.access.redhat.com/ubi9/python-314

# Standard S2I working dir
WORKDIR /opt/app-root

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/app-root/.local/bin:${PATH}"

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN chmod -R g+rwX /opt/app-root
