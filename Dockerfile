FROM python:3.8-slim-buster as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt



FROM python:3.8-slim-buster

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

ARG APP_USER=appuser
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}
RUN pip install --no-cache /wheels/*
COPY ./src /app
USER ${APP_USER}:${APP_USER}
CMD [ "uwsgi", "--http-socket", ":5000", "--plugin","python3", "--ini", "/app/uwsgi.ini" ]





