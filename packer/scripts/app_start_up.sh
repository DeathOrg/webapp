#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error: $1" >&2
    exit 1
}


# Main script execution
main() {

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

    "$PROJECT_LOC"/setup.sh "$PROJECT_LOC"

    sudo systemctl daemon-reload || handle_error "Failed to reload systemd."
    sudo systemctl enable webapp.service || handle_error "Failed to enable webapp.service."

    # Restart the webapp service in the background and continue
    sudo systemctl restart webapp.service &
    echo "Service restart initiated. Continuing with the script..."

    sudo systemctl status webapp.service || handle_error "Failed to check webapp.service status."

    sleep 150

    ls -la "$PROJECT_LOC"/myapp/migrations
}

# Execute the main function
main
