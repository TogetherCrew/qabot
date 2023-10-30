FROM python:3.10-slim-bullseye AS prod

ENV PYTHONFAULTHANDLER=1 \
PYTHONUNBUFFERED=1 \
PYTHONHASHSEED=random

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY . /project/

WORKDIR /project

RUN pdm export --format requirements --without-hashes > requirements.txt
RUN pip install -r requirements.txt

CMD ["python","main.py"]