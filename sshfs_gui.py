#!/usr/bin/env python3
"""
SSHFS GUI - Graphical interface for mounting remote filesystems via SSHFS
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QSpinBox, QFileDialog, QMessageBox, QLabel, QHeaderView,
    QMenu, QAction, QSystemTrayIcon, QStyle, QCheckBox, QComboBox,
    QGroupBox, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QColor


class Connection:
    """Represents an SSHFS connection configuration"""
    def __init__(self, name: str = "", host: str = "", port: int = 22,
                 username: str = "", remote_path: str = "/",
                 local_mount_point: str = "", ssh_key: str = "",
                 extra_options: str = ""):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.remote_path = remote_path
        self.local_mount_point = local_mount_point
        self.ssh_key = ssh_key
        self.extra_options = extra_options
        self.is_mounted = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "remote_path": self.remote_path,
            "local_mount_point": self.local_mount_point,
            "ssh_key": self.ssh_key,
            "extra_options": self.extra_options
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Connection':
        return cls(
            name=data.get("name", ""),
            host=data.get("host", ""),
            port=data.get("port", 22),
            username=data.get("username", ""),
            remote_path=data.get("remote_path", "/"),
            local_mount_point=data.get("local_mount_point", ""),
            ssh_key=data.get("ssh_key", ""),
            extra_options=data.get("extra_options", "")
        )


class ConnectionDialog(QDialog):
    """Dialog for adding/editing connections"""
    def __init__(self, parent=None, connection: Optional[Connection] = None):
        super().__init__(parent)
        self.connection = connection or Connection()
        self.setup_ui()
        self.load_connection_data()

    def setup_ui(self):
        self.setWindowTitle("Connection Settings" if self.connection.name else "New Connection")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Basic settings group
        basic_group = QGroupBox("Basic Settings")
        basic_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("My Server")
        basic_layout.addRow("Connection Name:", self.name_edit)

        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("example.com or 192.168.1.100")
        basic_layout.addRow("Host:", self.host_edit)

        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(22)
        basic_layout.addRow("Port:", self.port_spin)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("username")
        basic_layout.addRow("Username:", self.username_edit)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # Path settings group
        path_group = QGroupBox("Path Settings")
        path_layout = QFormLayout()

        self.remote_path_edit = QLineEdit()
        self.remote_path_edit.setPlaceholderText("/home/user or /var/www")
        path_layout.addRow("Remote Path:", self.remote_path_edit)

        mount_layout = QHBoxLayout()
        self.local_mount_edit = QLineEdit()
        self.local_mount_edit.setPlaceholderText("/mnt/remote")
        mount_layout.addWidget(self.local_mount_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_mount_point)
        mount_layout.addWidget(browse_btn)
        path_layout.addRow("Local Mount Point:", mount_layout)

        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        # SSH settings group
        ssh_group = QGroupBox("SSH Settings")
        ssh_layout = QFormLayout()

        key_layout = QHBoxLayout()
        self.ssh_key_edit = QLineEdit()
        self.ssh_key_edit.setPlaceholderText("~/.ssh/id_rsa (optional)")
        key_layout.addWidget(self.ssh_key_edit)
        key_browse_btn = QPushButton("Browse...")
        key_browse_btn.clicked.connect(self.browse_ssh_key)
        key_layout.addWidget(key_browse_btn)
        ssh_layout.addRow("SSH Key:", key_layout)

        self.extra_options_edit = QLineEdit()
        self.extra_options_edit.setPlaceholderText("-o reconnect,ServerAliveInterval=15")
        ssh_layout.addRow("Extra Options:", self.extra_options_edit)

        ssh_group.setLayout(ssh_layout)
        layout.addWidget(ssh_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_connection)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def load_connection_data(self):
        self.name_edit.setText(self.connection.name)
        self.host_edit.setText(self.connection.host)
        self.port_spin.setValue(self.connection.port)
        self.username_edit.setText(self.connection.username)
        self.remote_path_edit.setText(self.connection.remote_path)
        self.local_mount_edit.setText(self.connection.local_mount_point)
        self.ssh_key_edit.setText(self.connection.ssh_key)
        self.extra_options_edit.setText(self.connection.extra_options)

    def browse_mount_point(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Mount Point",
            os.path.expanduser("~")
        )
        if directory:
            self.local_mount_edit.setText(directory)

    def browse_ssh_key(self):
        ssh_dir = os.path.expanduser("~/.ssh")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select SSH Key",
            ssh_dir if os.path.exists(ssh_dir) else os.path.expanduser("~"),
            "All Files (*)"
        )
        if file_path:
            self.ssh_key_edit.setText(file_path)

    def save_connection(self):
        # Validate required fields
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Connection name is required.")
            self.name_edit.setFocus()
            return

        if not self.host_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Host is required.")
            self.host_edit.setFocus()
            return

        if not self.username_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Username is required.")
            self.username_edit.setFocus()
            return

        if not self.local_mount_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Local mount point is required.")
            self.local_mount_edit.setFocus()
            return

        # Update connection object
        self.connection.name = self.name_edit.text().strip()
        self.connection.host = self.host_edit.text().strip()
        self.connection.port = self.port_spin.value()
        self.connection.username = self.username_edit.text().strip()
        self.connection.remote_path = self.remote_path_edit.text().strip() or "/"
        self.connection.local_mount_point = self.local_mount_edit.text().strip()
        self.connection.ssh_key = self.ssh_key_edit.text().strip()
        self.connection.extra_options = self.extra_options_edit.text().strip()

        self.accept()


class SSHFSManager:
    """Handles SSHFS mount/unmount operations"""

    @staticmethod
    def check_sshfs_installed() -> bool:
        """Check if sshfs is installed"""
        try:
            result = subprocess.run(
                ["which", "sshfs"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def is_mounted(mount_point: str) -> bool:
        """Check if a path is currently mounted"""
        try:
            result = subprocess.run(
                ["mountpoint", "-q", mount_point],
                capture_output=True
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def mount(connection: Connection) -> tuple[bool, str]:
        """Mount an SSHFS connection"""
        mount_point = os.path.expanduser(connection.local_mount_point)

        # Create mount point if it doesn't exist
        try:
            os.makedirs(mount_point, exist_ok=True)
        except Exception as e:
            return False, f"Failed to create mount point: {e}"

        # Check if already mounted
        if SSHFSManager.is_mounted(mount_point):
            return False, "Mount point is already in use"

        # Build sshfs command
        remote = f"{connection.username}@{connection.host}:{connection.remote_path}"
        cmd = ["sshfs", remote, mount_point, "-p", str(connection.port)]

        # Add SSH key if specified
        if connection.ssh_key:
            key_path = os.path.expanduser(connection.ssh_key)
            if os.path.exists(key_path):
                cmd.extend(["-o", f"IdentityFile={key_path}"])

        # Add extra options
        if connection.extra_options:
            for opt in connection.extra_options.split():
                cmd.append(opt)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return True, "Successfully mounted"
            else:
                error = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                return False, f"Mount failed: {error}"
        except subprocess.TimeoutExpired:
            return False, "Mount operation timed out (30s)"
        except Exception as e:
            return False, f"Mount error: {e}"

    @staticmethod
    def unmount(connection: Connection) -> tuple[bool, str]:
        """Unmount an SSHFS connection"""
        mount_point = os.path.expanduser(connection.local_mount_point)

        if not SSHFSManager.is_mounted(mount_point):
            return True, "Not mounted"

        try:
            # Try fusermount first (preferred for FUSE filesystems)
            result = subprocess.run(
                ["fusermount", "-u", mount_point],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True, "Successfully unmounted"

            # Fallback to umount
            result = subprocess.run(
                ["umount", mount_point],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True, "Successfully unmounted"

            error = result.stderr.strip() or "Unknown error"
            return False, f"Unmount failed: {error}"
        except subprocess.TimeoutExpired:
            return False, "Unmount operation timed out"
        except Exception as e:
            return False, f"Unmount error: {e}"


class MainWindow(QMainWindow):
    """Main application window"""

    CONFIG_FILE = os.path.expanduser("~/.config/sshfs-gui/connections.json")

    def __init__(self):
        super().__init__()
        self.connections: List[Connection] = []
        self.setup_ui()
        self.load_connections()
        self.check_sshfs()
        self.start_status_timer()

    def setup_ui(self):
        self.setWindowTitle("SSHFS Manager")
        self.setMinimumSize(800, 500)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        add_btn = QPushButton("Add Connection")
        add_btn.clicked.connect(self.add_connection)
        toolbar_layout.addWidget(add_btn)

        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_connection)
        toolbar_layout.addWidget(edit_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_connection)
        toolbar_layout.addWidget(remove_btn)

        toolbar_layout.addStretch()

        mount_btn = QPushButton("Mount")
        mount_btn.clicked.connect(self.mount_selected)
        toolbar_layout.addWidget(mount_btn)

        unmount_btn = QPushButton("Unmount")
        unmount_btn.clicked.connect(self.unmount_selected)
        toolbar_layout.addWidget(unmount_btn)

        refresh_btn = QPushButton("Refresh Status")
        refresh_btn.clicked.connect(self.refresh_status)
        toolbar_layout.addWidget(refresh_btn)

        layout.addLayout(toolbar_layout)

        # Connection table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Host", "Remote Path", "Local Mount", "Status", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.doubleClicked.connect(self.edit_connection)
        layout.addWidget(self.table)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

    def check_sshfs(self):
        """Check if sshfs is installed and show warning if not"""
        if not SSHFSManager.check_sshfs_installed():
            QMessageBox.warning(
                self,
                "SSHFS Not Found",
                "SSHFS is not installed on this system.\n\n"
                "Please install it using:\n"
                "  Ubuntu/Debian: sudo apt install sshfs\n"
                "  Fedora: sudo dnf install fuse-sshfs\n"
                "  Arch: sudo pacman -S sshfs"
            )

    def start_status_timer(self):
        """Start timer to periodically refresh mount status"""
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.refresh_status)
        self.status_timer.start(5000)  # Refresh every 5 seconds

    def load_connections(self):
        """Load connections from config file"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.connections = [Connection.from_dict(c) for c in data]
        except Exception as e:
            QMessageBox.warning(
                self, "Load Error",
                f"Failed to load connections: {e}"
            )
        self.refresh_table()

    def save_connections(self):
        """Save connections to config file"""
        try:
            config_dir = os.path.dirname(self.CONFIG_FILE)
            os.makedirs(config_dir, exist_ok=True)
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump([c.to_dict() for c in self.connections], f, indent=2)
        except Exception as e:
            QMessageBox.warning(
                self, "Save Error",
                f"Failed to save connections: {e}"
            )

    def refresh_table(self):
        """Refresh the connection table"""
        self.table.setRowCount(len(self.connections))

        for row, conn in enumerate(self.connections):
            # Update mount status
            mount_point = os.path.expanduser(conn.local_mount_point)
            conn.is_mounted = SSHFSManager.is_mounted(mount_point)

            # Name
            self.table.setItem(row, 0, QTableWidgetItem(conn.name))

            # Host
            host_text = f"{conn.username}@{conn.host}:{conn.port}"
            self.table.setItem(row, 1, QTableWidgetItem(host_text))

            # Remote path
            self.table.setItem(row, 2, QTableWidgetItem(conn.remote_path))

            # Local mount
            self.table.setItem(row, 3, QTableWidgetItem(conn.local_mount_point))

            # Status
            status_item = QTableWidgetItem("Mounted" if conn.is_mounted else "Not Mounted")
            status_item.setForeground(
                QColor("green") if conn.is_mounted else QColor("gray")
            )
            self.table.setItem(row, 4, status_item)

            # Quick action button
            action_btn = QPushButton("Unmount" if conn.is_mounted else "Mount")
            action_btn.clicked.connect(lambda checked, r=row: self.toggle_mount(r))
            self.table.setCellWidget(row, 5, action_btn)

    def refresh_status(self):
        """Refresh mount status for all connections"""
        for row, conn in enumerate(self.connections):
            mount_point = os.path.expanduser(conn.local_mount_point)
            conn.is_mounted = SSHFSManager.is_mounted(mount_point)

            # Update status cell
            status_item = QTableWidgetItem("Mounted" if conn.is_mounted else "Not Mounted")
            status_item.setForeground(
                QColor("green") if conn.is_mounted else QColor("gray")
            )
            self.table.setItem(row, 4, status_item)

            # Update action button
            action_btn = self.table.cellWidget(row, 5)
            if action_btn:
                action_btn.setText("Unmount" if conn.is_mounted else "Mount")

    def get_selected_row(self) -> int:
        """Get currently selected row index"""
        selection = self.table.selectedItems()
        if selection:
            return selection[0].row()
        return -1

    def add_connection(self):
        """Add a new connection"""
        dialog = ConnectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.connections.append(dialog.connection)
            self.save_connections()
            self.refresh_table()
            self.statusBar.showMessage(f"Added connection: {dialog.connection.name}")

    def edit_connection(self):
        """Edit selected connection"""
        row = self.get_selected_row()
        if row < 0:
            QMessageBox.information(self, "Info", "Please select a connection to edit.")
            return

        conn = self.connections[row]
        dialog = ConnectionDialog(self, conn)
        if dialog.exec_() == QDialog.Accepted:
            self.save_connections()
            self.refresh_table()
            self.statusBar.showMessage(f"Updated connection: {conn.name}")

    def remove_connection(self):
        """Remove selected connection"""
        row = self.get_selected_row()
        if row < 0:
            QMessageBox.information(self, "Info", "Please select a connection to remove.")
            return

        conn = self.connections[row]

        # Confirm removal
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove '{conn.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Unmount if mounted
            if conn.is_mounted:
                SSHFSManager.unmount(conn)

            self.connections.pop(row)
            self.save_connections()
            self.refresh_table()
            self.statusBar.showMessage(f"Removed connection: {conn.name}")

    def toggle_mount(self, row: int):
        """Toggle mount state for a connection"""
        if row < 0 or row >= len(self.connections):
            return

        conn = self.connections[row]
        if conn.is_mounted:
            self.unmount_connection(conn)
        else:
            self.mount_connection(conn)

    def mount_selected(self):
        """Mount selected connection"""
        row = self.get_selected_row()
        if row < 0:
            QMessageBox.information(self, "Info", "Please select a connection to mount.")
            return
        self.mount_connection(self.connections[row])

    def unmount_selected(self):
        """Unmount selected connection"""
        row = self.get_selected_row()
        if row < 0:
            QMessageBox.information(self, "Info", "Please select a connection to unmount.")
            return
        self.unmount_connection(self.connections[row])

    def mount_connection(self, conn: Connection):
        """Mount a specific connection"""
        self.statusBar.showMessage(f"Mounting {conn.name}...")
        QApplication.processEvents()

        success, message = SSHFSManager.mount(conn)

        if success:
            self.statusBar.showMessage(f"Mounted: {conn.name}")
            conn.is_mounted = True
        else:
            QMessageBox.warning(self, "Mount Error", message)
            self.statusBar.showMessage(f"Mount failed: {conn.name}")

        self.refresh_status()

    def unmount_connection(self, conn: Connection):
        """Unmount a specific connection"""
        self.statusBar.showMessage(f"Unmounting {conn.name}...")
        QApplication.processEvents()

        success, message = SSHFSManager.unmount(conn)

        if success:
            self.statusBar.showMessage(f"Unmounted: {conn.name}")
            conn.is_mounted = False
        else:
            QMessageBox.warning(self, "Unmount Error", message)
            self.statusBar.showMessage(f"Unmount failed: {conn.name}")

        self.refresh_status()

    def closeEvent(self, event):
        """Handle window close"""
        # Check for mounted connections
        mounted = [c for c in self.connections if c.is_mounted]
        if mounted:
            reply = QMessageBox.question(
                self, "Mounted Connections",
                f"There are {len(mounted)} mounted connection(s).\n"
                "Do you want to unmount them before closing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.Yes:
                for conn in mounted:
                    SSHFSManager.unmount(conn)

        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SSHFS Manager")
    app.setOrganizationName("SSHFS-GUI")

    # Set application style
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
