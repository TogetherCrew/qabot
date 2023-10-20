FROM python:3.10-slim-bullseye AS base

ENV PYTHONFAULTHANDLER=1 \
PYTHONUNBUFFERED=1 \
PYTHONHASHSEED=random

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock /project/
#COPY . /project/

# install dependencies and project into the local packages directory
WORKDIR /project
RUN mkdir __pypackages__ && pdm sync --prod --no-editable --fail-fast


FROM python:3.10-slim-bullseye

ENV PYTHONPATH=/project/pkgs

COPY . /project/pkgs/

COPY --from=base /project/__pypackages__/3.10/lib /project/pkgs

# retrieve executables
COPY --from=base /project/__pypackages__/3.10/bin/* /bin/


WORKDIR /project/pkgs

CMD ["python","src/api.py"]
