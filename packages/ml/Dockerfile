FROM python:3.10-slim-bullseye AS base

ENV PYTHONFAULTHANDLER=1 \
PYTHONUNBUFFERED=1 \
PYTHONHASHSEED=random

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml /project/

# install dependencies and project into the local packages directory
WORKDIR /project
RUN pdm install


FROM python:3.10-slim-bullseye as prod

COPY . /project/
WORKDIR /project/

CMD ["python","src/api.py"]