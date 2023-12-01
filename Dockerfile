ARG PYTHON_VERSION=3.8
FROM --platform=${TARGETPLATFORM:-linux/amd64} python:${PYTHON_VERSION}-slim-buster as build

RUN apt-get update && \
    apt-get install -y build-essential cmake ca-certificates libgl1-mesa-glx && \
    apt-get install -y ffmpeg

RUN python3 -m pip install --upgrade pip

# Add non root user
RUN addgroup --system app && adduser app --system --ingroup app
RUN chown app /home/app

USER app

ENV PATH=$PATH:/home/app/.local/bin

WORKDIR /home/app/

COPY --chown=app:app monitorInputBucket.py           .
COPY --chown=app:app dynamodb.py           .
COPY --chown=app:app s3.py   .
COPY --chown=app:app .env   .
COPY --chown=app:app encoding   .
COPY --chown=app:app csvUtil.py   .
USER app

RUN mkdir -p face-recognition
RUN touch ./face-recognition/__init__.py
WORKDIR /home/app/face-recognition/
COPY --chown=app:app face-recognition/requirements.txt	.
RUN pip install --no-cache-dir -r requirements.txt

USER root
COPY --chown=app:app face-recognition/   .

FROM build as test

ARG TEST_COMMAND=tox
ARG TEST_ENABLED=true
RUN [ "$TEST_ENABLED" = "false" ] && echo "skipping tests" || eval "$TEST_COMMAND"

FROM build as ship
WORKDIR /home/app/

USER app

HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1

CMD ["python", "monitorInputBucket.py"]

