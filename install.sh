#!/bin/bash

# Check for Python and pip
echo "Checking for Python and pip..."

# Check if Python 3 is installed
if ! command -v python3 &>/dev/null; then
    echo "Python3 is not installed. Please install Python3."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &>/dev/null; then
    echo "pip is not installed. Installing pip..."
    sudo apt update
    sudo apt install -y python3-pip
fi

# Install python3-venv if not installed (for creating virtual environment)
echo "Installing python3-venv..."
sudo apt install -y python3-venv

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Check if the RSA key exists, and if not, generate it
if [ ! -f "server.key" ]; then
    echo "Generating RSA key for the SSH server..."
    ssh-keygen -t rsa -b 2048 -f server.key -N ""
else
    echo "RSA key already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the honeypot
echo "Running the honeypot..."
python honeypot.py