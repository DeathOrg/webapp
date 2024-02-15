#!/bin/bash

set -e

source config/.env || { echo "Error: Unable to load environment variables from config.env"; exit 1; }

# Function to update settings file
update_settings_file() {
    local settings_file="$1"
    local public_ip="$2"
    if [ -f "$settings_file" ]; then
        python - << EOF
import re

# Read the contents of the settings file
with open("$settings_file", "r") as f:
    content = f.read()

# Update the ALLOWED_HOSTS setting with the public IP
if "$public_ip" == "localhost":
    content = re.sub(r"(ALLOWED_HOSTS\s*=\s*\[)[^\]]*\]", r"\1'localhost', '127.0.0.1']", content)
else:
    content = re.sub(r"(ALLOWED_HOSTS\s*=\s*\[)[^\]]*\]", r"\1'$public_ip']", content)

# Write the updated contents back to the file
with open("$settings_file", "w") as f:
    f.write(content)

print("Allowed hosts updated for $ENVIRONMENT environment.")
EOF
    else
        echo "Error: Django settings file not found at $settings_file"
        exit 1
    fi
}


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

echo "Sourcing virtual environment from: $PROJECT_PATH/venv/bin/activate"
source "$PROJECT_PATH"/venv/bin/activate
echo "Virtual environment activated"

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
python -m pip install -r requirements/requirements.txt -r requirements/dev-requirements.txt

# Apply migrations if necessary
if ! python manage.py showmigrations --plan | grep "No planned migration"; then
    python manage.py migrate
fi

# Check if there are pending migrations
if python manage.py makemigrations myapp --check | grep -q "No changes detected"; then
    echo "No pending migrations found."
else
    # SQL query to delete migration records for the myapp app
    SQL_QUERY="DELETE FROM django_migrations WHERE app='myapp';"

    # Execute the SQL query using MySQL command line client
    mysql -u"$DATABASE_USER" -p"$DATABASE_PASSWORD" -h "$DATABASE_HOST" "$DATABASE_NAME" -e "$SQL_QUERY"

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

if [ "$ENVIRONMENT" = "production" ]; then
    # Fetch the public IP of the VM
    PUBLIC_IP=$(curl -s http://whatismyip.akamai.com/)
    SETTINGS_FILE="$PROJECT_PATH"/webapp/settings.py
    update_settings_file "$SETTINGS_FILE" "$PUBLIC_IP"
else
    update_settings_file "$SETTINGS_FILE" "localhost"
fi

# Run the development server
python manage.py runserver "$PUBLIC_IP":"$APP_PORT"
