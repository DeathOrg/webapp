#!/bin/bash

set -e
pwd
project_loc="$1"
source "$project_loc"/config/.env || { echo "Error: Unable to load environment variables from config.env"; exit 1; }

cd "$PROJECT_PATH"
# Apply migrations if necessary
if ! python3.9 manage.py showmigrations --plan | grep "No planned migration"; then
    python3.9 manage.py migrate
fi

# Check if there are pending migrations
if python3.9 manage.py makemigrations myapp --check | grep -q "No changes detected"; then
    echo "No pending migrations found."
else
    # SQL query to delete migration records for the myapp app
    SQL_QUERY="DELETE FROM django_migrations WHERE app='myapp';"

    # Execute the SQL query using MySQL command line client
    mysql -u"$DATABASE_USER" -p"$DATABASE_PASSWORD" -h "$DATABASE_HOST" "$DATABASE_NAME" -e "$SQL_QUERY"

    # Check if the command executed successfully
    if [ $? -eq 0 ]; then
      echo "Migration records for myapp deleted successfully."
      python3.9 manage.py flush --no-input
      python3.9 manage.py makemigrations myapp
      python3.9 manage.py migrate
    else
      echo "Failed to delete migration records for myapp."
    fi
fi

# Run the development server
python3.9 manage.py runserver 0.0.0.0:"$APP_PORT"
