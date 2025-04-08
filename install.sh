#!/bin/bash

echo "Installing Honeygotchi..."

# Exit on error
set -e

# Step 1: Ensure system dependencies are installed
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

# Step 2: Setup virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 3: Install Python requirements
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Set up Cowrie honeypot
echo "Setting up Cowrie..."
python3 scripts/install_pots.py

# Step 5: Start Honeygotchi
echo "Launching Honeygotchi..."
python3 main.py

echo "✅ Honeygotchi installed and running!"