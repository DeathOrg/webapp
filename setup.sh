#!/bin/bash

set -e

# Check for Python
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed."
    exit 1
fi

# Check for existing virtual environment
if [ ! -d "venv" ]; then
    # Create virtual environment
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
python -m pip install -r requirements/requirements.txt -r requirements/dev-requirements.txt

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Run the development server
python manage.py runserver
