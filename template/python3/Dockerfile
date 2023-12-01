ARG PYTHON_VERSION=3.8
FROM --platform=${TARGETPLATFORM:-linux/amd64} ghcr.io/openfaas/classic-watchdog:0.2.3 as watchdog
FROM --platform=${TARGETPLATFORM:-linux/amd64} python:${PYTHON_VERSION}-alpine

ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Allows you to add additional packages via build-arg
ARG ADDITIONAL_PACKAGE

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog
RUN apk --no-cache add ca-certificates ${ADDITIONAL_PACKAGE}

# Install build dependencies for numpy
RUN apk --no-cache add \
    g++ \
    gcc \
    make \
    libc-dev \
    musl-dev \
    linux-headers \
    cython \
    ffmpeg \
    build-base

RUN apk --no-cache update && apk --no-cache upgrade

# Add non root user
RUN addgroup -S app && adduser app -S -G app

WORKDIR /home/app/

COPY index.py           .
COPY requirements.txt   .
COPY .env   .

RUN chown -R app /home/app && \
  mkdir -p /home/app/python && chown -R app /home/app
USER app
ENV PATH=$PATH:/home/app/.local/bin:/home/app/python/bin/
ENV PYTHONPATH=$PYTHONPATH:/home/app/python

RUN pip install -r requirements.txt --target=/home/app/python

RUN mkdir -p function
RUN touch ./function/__init__.py

WORKDIR /home/app/function/
COPY function/requirements.txt	.

COPY function/dynamodb.py .
COPY function/s3.py .
COPY function/.env /home/app/function/
COPY function/encoding /home/app/function/
COPY function/csvUtil.py .

RUN pip install -r requirements.txt --target=/home/app/python

WORKDIR /home/app/

USER root

COPY function           function

# Allow any user-id for OpenShift users.
RUN chown -R app:app ./ && \
  chmod -R 777 /home/app/python

USER app

ENV fprocess="python3 index.py"
EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
