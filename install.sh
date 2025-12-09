#!/bin/bash
# SSHFS GUI Installation Script

set -e

echo "=== SSHFS GUI Installer ==="
echo

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 first."
    exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    echo "Please install pip3 first (e.g., sudo apt install python3-pip)"
    exit 1
fi

# Check for sshfs
if ! command -v sshfs &> /dev/null; then
    echo "Warning: sshfs is not installed."
    echo "The application will run but won't be able to mount filesystems."
    echo
    echo "To install sshfs:"
    echo "  Ubuntu/Debian: sudo apt install sshfs"
    echo "  Fedora:        sudo dnf install fuse-sshfs"
    echo "  Arch:          sudo pacman -S sshfs"
    echo
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Make the main script executable
chmod +x sshfs_gui.py

# Create desktop entry
DESKTOP_FILE="$HOME/.local/share/applications/sshfs-gui.desktop"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=SSHFS Manager
Comment=Mount remote filesystems via SSHFS
Exec=python3 $SCRIPT_DIR/sshfs_gui.py
Icon=folder-remote
Terminal=false
Type=Application
Categories=System;FileTools;Network;
Keywords=ssh;sshfs;mount;remote;filesystem;
EOF

echo
echo "=== Installation Complete ==="
echo
echo "You can now:"
echo "  1. Run from terminal: python3 $SCRIPT_DIR/sshfs_gui.py"
echo "  2. Find 'SSHFS Manager' in your application menu"
echo
