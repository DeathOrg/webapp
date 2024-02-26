#!/bin/bash

sleep 10

# Function to handle errors
handle_error() {
    echo "Error: $1" >&2
    exit 1
}

# Update system
echo "Updating System..."
sudo yum update -y || handle_error "Failed to update system packages."
sudo yum upgrade -y

echo "Install mysql client..."
yum install mysql -y

# Install Python 3.9
echo "Installing Python 3.9..."
sudo yum install -y python39 || handle_error "Failed to install Python 3.9."

# Install pip for Python 3.9
echo "Installing pip for Python 3.9..."
sudo yum install -y python39-pip || handle_error "Failed to install pip for Python 3.9."

# Install Python and MySQL development packages
echo "Installing Python and MySQL development packages..."
sudo yum install -y python39-devel mysql-devel || handle_error "Failed to install Python and MySQL development packages."
sudo yum groupinstall -y "Development Tools" || handle_error "Failed to install development tools."
python3.9 -m pip install mysqlclient || handle_error "Failed to install mysqlclient."

# Upgrade pip
echo "Upgrading pip..."
python3.9 -m pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
#python3.9 -m pip install -r /tmp/requirements.txt
sudo /usr/bin/pip3.9 install -r /tmp/requirements.txt

echo "pip3.9 list..."
pip3.9 list

echo "python3.9 -m list output.."
python3.9 -m pip list

echo "Installing unzip..."
sudo yum install unzip -y
