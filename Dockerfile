#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.
#
# Build image:
# docker build -t nscheck.net .
#
# Run container:
# docker run --rm -it -p 8000:8000 --name nscheck.net nscheck.net:latest

ARG BASE_IMAGE_NAME=python:3.8-slim-buster

# Intermediate build container
FROM $BASE_IMAGE_NAME AS builder

ENV LANG=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive \
    # Extra python env
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_FORMAT="columns" \
    PIP_NO_BINARY=":all:" \
    PIP_CACHE_DIR="/tmp/pip" \
    PIP_TIMEOUT=60

RUN apt-get update && \
    apt-get install --assume-yes --no-install-recommends build-essential && \
    mkdir -p /app /venv && \
    chown -R nobody:nogroup /app /venv

WORKDIR /app
USER nobody:nogroup
COPY nscheck/ /app/nscheck
COPY ./config.py ./requirements.txt /app/
COPY ./config_docker.py /app/config_local.py
# Install Python deps
RUN python3 -m venv /venv && \
    /venv/bin/pip install -r /app/requirements.txt

#    /venv/bin/pip install -U pip setuptools wheel && \

# App container
FROM $BASE_IMAGE_NAME AS app

ENV LANG=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive \
    # Extra python env
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# copy in Python environment
COPY --from=builder /app /app
COPY --from=builder /venv /venv

USER nobody:nogroup
CMD [ \
    "/venv/bin/uwsgi", \
        "--master", \
        "--log-master", \
        "--http", "0.0.0:8000", \
        "--processes", "4", \
        "--manage-script-name", \
        "--mount", "/=nscheck:wsgi" \
]
EXPOSE 8000
