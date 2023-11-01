FROM python:3.10-slim-bullseye AS local

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random

# Install PDM
RUN pip install -U pip setuptools wheel && \
    pip install pdm

# Set the working directory
WORKDIR /project

# copy files
COPY pyproject.toml pdm.lock /project/

# Install dependencies and the project in the local directory
RUN mkdir __pypackages__ && pdm sync --prod --no-editable --fail-fast

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/project/pkgs

RUN mkdir -p /project/pkgs

# Move files and executables from the dependencies directory
RUN mv __pypackages__/3.10/lib/* /project/pkgs && \
    mv __pypackages__/3.10/bin/* /bin/

WORKDIR /project

# Default command to be executed when the container starts
#CMD ["python", "main.py"]
