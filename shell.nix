{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "sshfs-gui-dev";

  buildInputs = with pkgs; [
    # Python environment
    python3
    python3Packages.pyqt5
    python3Packages.pip
    python3Packages.pyinstaller

    # Qt dependencies
    qt5.qtbase
    qt5.wrapQtAppsHook

    # SSHFS for mounting
    sshfs

    # Build tools
    binutils
    patchelf
  ];

  # Set up Qt environment
  shellHook = ''
    export QT_QPA_PLATFORM_PLUGIN_PATH="${pkgs.qt5.qtbase.bin}/lib/qt-${pkgs.qt5.qtbase.version}/plugins/platforms"
    export QT_PLUGIN_PATH="${pkgs.qt5.qtbase.bin}/lib/qt-${pkgs.qt5.qtbase.version}/plugins"
    
    echo "SSHFS GUI Development Environment"
    echo "=================================="
    echo ""
    echo "Available commands:"
    echo "  python3 sshfs_gui.py  - Run the application"
    echo "  ./build.sh            - Build standalone binary"
    echo ""
    echo "Dependencies:"
    echo "  Python: $(python3 --version)"
    echo "  PyQt5:  $(python3 -c 'from PyQt5.QtCore import QT_VERSION_STR; print(QT_VERSION_STR)' 2>/dev/null || echo 'available')"
    echo "  SSHFS:  $(sshfs --version 2>&1 | head -1)"
    echo ""
  '';

  # Prevent Qt from complaining about missing plugins
  QT_QPA_PLATFORM = "xcb";
}
