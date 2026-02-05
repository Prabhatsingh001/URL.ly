# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
# libpq-dev is often needed for psycopg2 (PostgreSQL adapter), though we see sqlite3 primarily.
# gcc is needed for compiling some python packages.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Create a non-root user and switch to it
RUN addgroup --system django_group && adduser --system --ingroup django_group django_user
RUN chown -R django_user:django_group /app
USER django_user

# Collect static files (Moved to runtime/docker-compose because it requires env vars)
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Command to run the application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "UrlShortner.wsgi:application"]