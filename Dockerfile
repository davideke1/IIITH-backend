## Use an official Python runtime as a parent image
#FROM python:3.9-slim
#
## Set the working directory in the container
#WORKDIR /usr/src/app
#
## Install build tools and libraries
#RUN apt-get update && apt-get install -y \
#    build-essential \
#    python3-dev \
#    gcc \
#    && rm -rf /var/lib/apt/lists/*
#
## Copy the requirements file into the container
#COPY requirements-docker.txt ./
#
## Install any dependencies specified in requirements.txt
#RUN pip install --no-cache-dir -r requirements-docker.txt
#
## Copy the rest of the application's code into the container
#COPY . .
#
## Specify the command to run on container start
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Use the official Python image as the base image
FROM python:3.10.6

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /code


## Install build tools and libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*
#

# Install dependencies
RUN pip install --upgrade pip

RUN pip install uwsgi

COPY requirements-docker.txt /code/
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy the project files
COPY . /code/

# Create the log directory
RUN mkdir -p /code/logs && \
    mkdir -p /var/log/uwsgi && \
    chown www-data:www-data /code/logs && \
    chown www-data:www-data /var/log/uwsgi

# Expose port 8000 to the outside world
EXPOSE 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

#Start  server
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "CoreRoot.asgi:application"]
