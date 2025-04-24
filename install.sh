#!/bin/bash

# Ensure the script is run as root or with sudo privileges
if [ "$(id -u)" -ne 0 ]; then
    echo "Please run this script with sudo."
    exit 1
fi

# Install Python and pip if not already installed
echo "Checking for Python and pip..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Installing Python3..."
    apt-get update && apt-get install -y python3 python3-pip
fi

if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Installing pip3..."
    apt-get install -y python3-pip
fi

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Check if the dependencies were installed
if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully!"
else
    echo "Error installing dependencies."
    exit 1
fi

# Generate SSH key for the server if not present
if [ ! -f "server.key" ]; then
    echo "Generating SSH key..."
    ssh-keygen -t rsa -b 2048 -f server.key -N ""
fi

# Start the honeypot
echo "Starting the honeypot..."
python3 honeypot.py

# All set up
echo "Honeypot installation and startup complete."