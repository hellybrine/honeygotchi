#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" &>/dev/null
}

# Function to validate we're in the right directory
validate_project_directory() {
    if [ ! -f "honeypot.py" ] || [ ! -f "requirements.txt" ]; then
        print_error "This doesn't appear to be the Honeygotchi project directory."
        print_error "Make sure you're running this script from the project root."
        exit 1
    fi
}

# Function to install Python dependencies
install_python_dependencies() {
    print_status "Upgrading pip..."
    pip install --upgrade pip || {
        print_error "Failed to upgrade pip"
        exit 1
    }
    
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt || {
        print_error "Failed to install Python dependencies"
        print_error "Check requirements.txt and try again"
        exit 1
    }
}

# Function to generate SSH key
generate_ssh_key() {
    if [ ! -f "server.key" ]; then
        if ! command_exists ssh-keygen; then
            print_error "ssh-keygen not found. Please install OpenSSH client."
            exit 1
        fi
        
        print_status "Generating RSA key for the SSH server..."
        print_warning "Generating key with empty passphrase for automation"
        ssh-keygen -t rsa -b 2048 -f server.key -N "" -C "honeygotchi-$(date +%Y%m%d)" || {
            print_error "Failed to generate SSH key"
            exit 1
        }
        chmod 600 server.key
        print_status "SSH key generated successfully"
    else
        print_status "RSA key already exists, skipping generation"
    fi
}

main() {
    print_header "Setting Up Honeygotchi"
    
    validate_project_directory
    
    if ! command_exists python3; then
        print_status "Python3 not found. Attempting to install..."
        
        if command_exists apt; then
            sudo apt update && sudo apt install -y python3 python3-pip python3-venv
        elif command_exists yum; then
            sudo yum install -y python3 python3-pip
        elif command_exists dnf; then
            sudo dnf install -y python3 python3-pip
        elif command_exists pacman; then
            sudo pacman -S python python-pip
        else
            print_error "Unsupported package manager. Please install Python 3 manually."
            exit 1
        fi
    else
        print_status "Python3 found: $(python3 --version)"
    fi
    
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv || {
            print_error "Failed to create virtual environment"
            exit 1
        }
    else
        print_status "Virtual environment already exists"
    fi
    
    print_status "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    install_python_dependencies
    
    print_status "Creating project directories..."
    mkdir -p logs models data
    
    # Generate SSH key
    generate_ssh_key
    
    print_header "Installation Complete!"
    echo -e "${GREEN}Honeygotchi has been successfully installed!${NC}"
    echo
    echo "Features installed:"
    echo " ✓ PyTorch-based RL agent"
    echo " ✓ Adaptive deception engine" 
    echo " ✓ Realistic fake filesystem"
    echo " ✓ Multi-objective optimization"
    echo " ✓ Production model export"
    echo
    echo -e "To start Honeygotchi:${NC}"
    echo "1. Activate the virtual environment:"
    echo -e "source venv/bin/activate${NC}"
    echo "2. Run the honeypot:"
    echo -e "python3 honeypot.py${NC}"
    echo
    echo -e "To deactivate the virtual environment later:${NC}"
    echo "deactivate${NC}"
    echo
    print_warning "Remember to configure any settings before running in production!"
}

cleanup() {
    if [ $? -ne 0 ]; then
        print_error "Installation failed. Check the error messages above."
        echo "You may need to:"
        echo "- Install missing system dependencies"
        echo "- Check your internet connection"
        echo "- Run with appropriate permissions"
    fi
}

trap cleanup EXIT

main "$@"