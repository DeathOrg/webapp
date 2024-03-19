#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error: $1" >&2
    exit 1
}

handle_service_status_error() {
    echo "Error: $1" >&2
    exit 0
}

create_log_dir(){
  #create log dir
    if [ ! -d "$LOG_DIR" ]; then
        # Create the directory if it doesn't exist
        sudo mkdir -p "$LOG_DIR"
        echo "Created log directory: $LOG_DIR"

        # Set appropriate permissions
        sudo chown -R csye6225:csye6225 "$LOG_DIR"
        sudo chmod 750 "$LOG_DIR"
        echo "Set permissions for log directory: $LOG_DIR"
    else
        echo "Log directory already exists: $LOG_DIR"
    fi
}

# Main script execution
main() {
    # Setup web application
    echo "Setting up web application..."
    mkdir -p "$PROJECT_LOC"
    unzip webapp.zip -d "$PROJECT_LOC"
    chmod +x $PROJECT_LOC/setup.sh
    sudo mv /tmp/webapp.service /etc/systemd/system/webapp.service

    rm -rf /home/csye6225/webapp* __MACOSX
    rm -rf /home/csye6225/cloud/__MACOSX
    rm -rf "$PROJECT_LOC"/app_artifact
    rm -f "$PROJECT_LOC"/*.json

    create_log_dir

    sudo chown csye6225:csye6225 "$PROJECT_LOC"/setup.sh
    sudo chown -R csye6225:csye6225 "$PROJECT_LOC"
    sudo chmod -R 755 "$PROJECT_LOC"
    chmod +x "$PROJECT_LOC"/setup.sh
    sudo setenforce 0

    sudo systemctl daemon-reload || handle_error "Failed to reload systemd."
    sudo systemctl enable webapp.service || handle_error "Failed to enable webapp.service."
}

# Execute the main function
main
