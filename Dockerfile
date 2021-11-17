FROM python:3.8.2-slim-buster
WORKDIR /app
COPY ./requirements.txt requirements.txt
ARG APP_USER=appuser
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}
RUN apt-get update && apt-get install -y --no-install-recommends uwsgi uwsgi-plugin-python3 python3-distutils && rm -rf /var/lib/apt/lists/* && pip install -r requirements.txt
COPY ./src /app
USER ${APP_USER}:${APP_USER}
CMD [ "uwsgi", "--http-socket", ":5000", "--plugin","python3", "--ini", "/app/uwsgi.ini" ]

