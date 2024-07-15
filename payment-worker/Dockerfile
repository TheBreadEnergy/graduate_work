FROM python:3.12.2

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_ROOT_USER_ACTION=ignore \
  DOCKERIZE_VERSION="v0.7.0" \
  PYTHONDONTWRITEBYTECODE=1

WORKDIR /payment-worker

RUN pip install poetry && \
    poetry config virtualenvs.in-project true

COPY pyproject.toml .

RUN poetry install --without dev

COPY . .

CMD ["poetry", "run", "python", "src/main.py"]
