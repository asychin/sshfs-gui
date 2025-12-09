# SSHFS GUI Manager

A graphical user interface for mounting remote filesystems via SSHFS on Linux.

## Features

- Add, edit, and remove SSH connection configurations
- One-click mount/unmount of remote filesystems
- Automatic status monitoring (refreshes every 5 seconds)
- Persistent storage of connection settings
- Support for SSH key authentication
- Custom SSHFS options support
- Desktop integration (application menu entry)

## Requirements

- Linux operating system
- Python 3.6+
- PyQt5
- sshfs (fuse-sshfs)

## Installation

### 1. Install system dependencies

**Ubuntu/Debian:**
```bash
sudo apt install sshfs python3-pyqt5
```

**Fedora:**
```bash
sudo dnf install fuse-sshfs python3-qt5
```

**Arch Linux:**
```bash
sudo pacman -S sshfs python-pyqt5
```

### 2. Run the installer

```bash
cd sshfs-gui
./install.sh
```

Or manually:
```bash
pip3 install --user PyQt5
python3 sshfs_gui.py
```

## Usage

1. Launch the application from terminal or application menu
2. Click "Add Connection" to create a new connection
3. Fill in the connection details:
   - **Connection Name**: A friendly name for the connection
   - **Host**: Server hostname or IP address
   - **Port**: SSH port (default: 22)
   - **Username**: SSH username
   - **Remote Path**: Path on the remote server to mount
   - **Local Mount Point**: Local directory where files will be accessible
   - **SSH Key**: (Optional) Path to SSH private key
   - **Extra Options**: (Optional) Additional sshfs options
4. Click "Save" to save the connection
5. Select a connection and click "Mount" or use the quick action button

## Configuration

Connection settings are stored in:
```
~/.config/sshfs-gui/connections.json
```

## Troubleshooting

### "SSHFS Not Found" error
Install sshfs using your package manager (see Installation section).

### "Permission denied" when mounting
- Ensure your user is in the `fuse` group: `sudo usermod -a -G fuse $USER`
- Log out and log back in for group changes to take effect

### Mount point busy
- Close any file managers or terminals using the mount point
- Try: `fusermount -u /path/to/mount`

### Connection timeout
- Verify the server is reachable: `ssh user@host`
- Check firewall settings
- Try adding `-o ServerAliveInterval=15` to extra options

## License

MIT License
