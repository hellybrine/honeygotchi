#!/bin/bash
# Build script for Honeygotchi executable

set -e

echo "🧠 Building Honeygotchi executable..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Create build directory
BUILD_DIR="dist"
mkdir -p "$BUILD_DIR"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.spec

# Build executable
echo "🔨 Building executable..."
pyinstaller honeygotchi.spec

# Copy config file to dist if it exists
if [ -f "config.yaml" ]; then
    echo "📋 Copying config.yaml to dist..."
    cp config.yaml "$BUILD_DIR/"
fi

# Create a README for the executable
cat > "$BUILD_DIR/README.txt" << EOF
Honeygotchi - SSH Honeypot with Reinforcement Learning
=====================================================

Usage:
  ./honeygotchi [options]

Options:
  --config PATH          Path to configuration file (YAML)
  --port PORT            SSH port (default: 2222)
  --metrics-port PORT    Prometheus metrics port (default: 9090)
  --log-dir PATH         Log directory (default: logs)
  --host-key PATH        SSH host key file (default: ssh_host_key)
  --generate-key         Force generate new SSH host key
  --epsilon FLOAT        RL exploration rate (default: 0.3)
  --learning-rate FLOAT  RL learning rate (default: 0.1)
  --clear-state          Clear saved RL state

Configuration:
  The executable will look for config.yaml in:
  1. Current directory
  2. ~/.honeygotchi/config.yaml
  3. /etc/honeygotchi/config.yaml

  If no config file is found, defaults will be used.

Files Created:
  - ssh_host_key: SSH host key (auto-generated if missing)
  - rl_state.json: RL agent state (saved periodically)
  - logs/honeygotchi.log: Application logs

For more information, visit: https://github.com/yourusername/honeygotchi
EOF

echo "✅ Build complete! Executable is in: $BUILD_DIR/honeygotchi"
echo ""
echo "To run:"
echo "  cd $BUILD_DIR"
echo "  ./honeygotchi"
