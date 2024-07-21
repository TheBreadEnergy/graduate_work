FROM python:3.12-buster

WORKDIR /opt/app


ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_ROOT_USER_ACTION=ignore \
  PYTHONDONTWRITEBYTECODE=1

RUN groupadd -r fastapi && useradd -d /opt/app -r -g fastapi fastapi \
    && chown fastapi:fastapi -R /opt/app


COPY requirements.txt requirements.txt

COPY docker-entrypoint.sh docker-entrypoint.sh

RUN apt-get update  \
    && apt-get -y install netcat-traditional \
    && python -m pip install --upgrade pip && pip install -r requirements.txt

RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

USER fastapi

ENTRYPOINT ["/opt/app/docker-entrypoint.sh"]


