#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error: $1" >&2
    exit 1
}

# Start and enable MySQL service
start_mysql_service() {
    echo "Starting and enabling MySQL service..."
    sudo systemctl start mysqld || handle_error "Failed to start MySQL service."
    sudo systemctl enable mysqld || handle_error "Failed to enable MySQL service."
}

# Set MySQL root password
set_mysql_root_password() {
    echo "Setting MySQL root password..."
    echo "mysql root password for creating database here: $MYSQL_ROOT_PASSWORD"
    mysqladmin -u root password "$MYSQL_ROOT_PASSWORD" || handle_error "Failed to set MySQL root password."
}

# Create MySQL database and user
create_mysql_database_user() {
    echo "Creating MySQL database and user..."
    echo "Database name: $DATABASE_NAME"
    echo "Database user: $DATABASE_USER"
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<MYSQL_SCRIPT || handle_error "Failed to execute MySQL tasks."
    CREATE DATABASE IF NOT EXISTS \`$DATABASE_NAME\`;
    CREATE USER IF NOT EXISTS '$DATABASE_USER'@'localhost' IDENTIFIED BY '$DATABASE_PASSWORD';
    GRANT ALL PRIVILEGES ON \`$DATABASE_NAME\`.* TO '$DATABASE_USER'@'localhost';
    FLUSH PRIVILEGES;
MYSQL_SCRIPT
}

# Main script execution
main() {
    # Ensure MySQL service is started and enabled
    start_mysql_service

    # Set MySQL root password
    set_mysql_root_password

    # Create MySQL database and user
    create_mysql_database_user

    # Setup web application
    echo "Setting up web application..."
    mkdir -p "$PROJECT_LOC"
    unzip webapp.zip -d "$PROJECT_LOC"
    chmod +x $PROJECT_LOC/setup.sh
    sudo mv /tmp/webapp.service /etc/systemd/system/webapp.service

    echo "DATABASE_PASSWORD=$DATABASE_PASSWORD" >> "$PROJECT_LOC"/config/.env
    rm -rf /home/csye6225/webapp* __MACOSX
    rm -rf /home/csye6225/cloud/__MACOSX
    rm -rf "$PROJECT_LOC"/app_artifact
    rm -f "$PROJECT_LOC"/*.json

    sudo chown csye6225:csye6225 "$PROJECT_LOC"/setup.sh
    sudo chown -R csye6225:csye6225 "$PROJECT_LOC"
    sudo chmod -R 755 "$PROJECT_LOC"
    chmod +x "$PROJECT_LOC"/setup.sh
    sudo setenforce 0

    sudo systemctl daemon-reload || handle_error "Failed to reload systemd."
    sudo systemctl enable webapp.service || handle_error "Failed to enable webapp.service."
    sudo systemctl restart webapp.service || handle_error "Failed to restart webapp.service."
    sudo systemctl status webapp.service || handle_error "Failed to check webapp.service status."

    ls -la "$PROJECT_LOC"/myapp/migrations
}

# Execute the main function
main
