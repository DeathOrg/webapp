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

# Check if there are pending migrations
if python manage.py makemigrations --check myapp 2>&1 | grep -q "No changes detected"; then
    echo "No pending migrations found."
else
    # Define database credentials
    DB_NAME="webApp"
    DB_USER="dev-1"
    DB_PASSWORD="DreamBig@08"
    DB_HOST="localhost"

    # SQL query to delete migration records for the myapp app
    SQL_QUERY="DELETE FROM django_migrations WHERE app='myapp';"

    # Execute the SQL query using MySQL command line client
    mysql -u"$DB_USER" -p"$DB_PASSWORD" -h "$DB_HOST" "$DB_NAME" -e "$SQL_QUERY"

    # Check if the command executed successfully
    if [ $? -eq 0 ]; then
      echo "Migration records for myapp deleted successfully."
      python manage.py flush --no-input
      python manage.py makemigrations myapp
      python manage.py migrate
    else
      echo "Failed to delete migration records for myapp."
    fi
fi

# Run the development server
python manage.py runserver
