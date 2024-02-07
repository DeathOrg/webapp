#!/bin/bash

set -e

source config/.secret-env || { echo "Error: Unable to load environment variables from config.env"; exit 1; }

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
source "$PROJECT_PATH"/venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
python -m pip install -r requirements/requirements.txt -r requirements/dev-requirements.txt

# Check if there are pending migrations
if python manage.py makemigrations --check myapp 2>&1 | grep -q "No changes detected"; then
    echo "No pending migrations found."
else
    # SQL query to delete migration records for the myapp app
    SQL_QUERY="DELETE FROM django_migrations WHERE app='$DB_NAME';"

    # Execute the SQL query using MySQL command line client
    mysql -u"$DB_USER" -p"$DB_PASSWORD" -h "$DB_HOST" "$DB_NAME" -e "$SQL_QUERY"

    # Check if the command executed successfully
    # shellcheck disable=SC2181
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
python manage.py runserver "$APP_HOSTNAME":"$APP_PORT"
