#!/bin/bash

set -e

echo "=== Setting Up Honeygotchi ==="

# Check for Python 3
if ! command -v python3 &>/dev/null; then
    echo "Python3 is not installed. Attempting to install..."
    if command -v apt &>/dev/null; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3 python3-pip
    else
        echo "Unsupported OS. Please install Python 3 manually."
        exit 1
    fi
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

mkdir -p logs models data

# Generate SSH key if not exists
if [ ! -f "server.key" ]; then
    echo "Generating RSA key for the SSH server..."
    ssh-keygen -t rsa -b 2048 -f server.key -N ""
else
    echo "RSA key already exists."
fi

echo "Enhanced Honeygotchi setup complete!"
echo "Features:"
echo "  - PyTorch-based RL agent"
echo "  - Adaptive deception engine"
echo "  - Realistic fake filesystem"
echo "  - Multi-objective optimization"
echo "  - Production model export"
echo ""
echo "Starting the enhanced honeypot..."
python3 honeypot.py