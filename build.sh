#!/bin/bash
# SSHFS GUI Build Script - Creates standalone binary using PyInstaller

set -e

echo "=== SSHFS GUI Build Script ==="
echo

# Check for PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec

# Build the application
echo "Building SSHFS GUI..."
pyinstaller \
    --name="sshfs-gui" \
    --onefile \
    --windowed \
    --noconfirm \
    --clean \
    sshfs_gui.py

echo
echo "=== Build Complete ==="
echo
echo "Binary location: dist/sshfs-gui"
echo
echo "To run: ./dist/sshfs-gui"
echo
echo "To install system-wide:"
echo "  sudo cp dist/sshfs-gui /usr/local/bin/"
echo
