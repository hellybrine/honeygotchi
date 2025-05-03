#!/bin/bash

set -e

echo "=== Setting Up Honeygotchi ==="

# Check for Python 3
if ! command -v python3 &>/dev/null; then
    echo "Python3 is not installed. Attempting to install..."
    if command -v apt &>/dev/null; then
        sudo apt update
        sudo apt install -y python3
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3
    else
        echo "Unsupported OS. Please install Python 3 manually."
        exit 1
    fi
fi

# Check for pip3
if ! command -v pip3 &>/dev/null; then
    echo "pip3 is not installed. Attempting to install..."
    if command -v apt &>/dev/null; then
        sudo apt update
        sudo apt install -y python3-pip
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3-pip
    else
        echo "Unsupported OS. Please install pip3 manually."
        exit 1
    fi
fi

if ! python3 -m venv --help &>/dev/null; then
    echo "python3-venv is not installed. Installing..."
    if command -v apt &>/dev/null; then
        sudo apt install -y python3-venv
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3-venv
    else
        echo "Unsupported OS. Please install python3-venv manually."
        exit 1
    fi
fi

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ ! -f "server.key" ]; then
    echo "Generating RSA key for the SSH server..."
    ssh-keygen -t rsa -b 2048 -f server.key -N ""
else
    echo "RSA key already exists."
fi

if [ ! -d "models" ]; then
    mkdir models
fi

if [ ! -f "models/randomforest_classifier.pkl" ]; then
    echo "Trained ML model not found. Training model..."
    python3 -c "import model; model.train_model()"
else
    echo "Trained ML model already exists."
fi

echo "All set! Starting the honeypot..."
python3 honeypot.py