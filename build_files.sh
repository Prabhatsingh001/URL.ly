#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Install Tailwind CSS (uses Node + Tailwind CLI)
python manage.py tailwind install

# Build Tailwind CSS
python manage.py tailwind build

# Collect static files for deployment
python manage.py collectstatic --noinput

# Move static files to Vercel's expected output folder
mkdir -p staticfiles_build
cp -r staticfiles/* staticfiles_build/