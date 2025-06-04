# Pull official base image
FROM python:3.10-alpine

# The /app directory should act as the main application directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install psycopg2 (Postgres) & Pillow dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev

# Copy requirements.txt to working directory
COPY requirements.txt ./

# Install all the dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt # The -r flag tells pip to read and install the packages in the file.

# Copy project files to working directory
COPY . ./

# Expose port 8000 of the container (this setting is only useful when using Docker Desktop to create containers)
EXPOSE 8000

# Make migrations for existing models
RUN python manage.py makemigrations
RUN python manage.py migrate

# apk (Alpine Package Keeper) is the package manager of alpine distribution.
# Alpine is a Linux distribution - an operating system that includes the Linux kernel for its kernel functionality.
# Above we use "apk" to install the psycopg2 dependencies into the environment directly.

