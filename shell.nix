{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "sshfs-gui-dev";

  buildInputs = with pkgs; [
    # Python (base only - PyQt5/PyInstaller come from venv to avoid Nix Qt plugin issues)
    python3
    python3Packages.pip
    python3Packages.virtualenv

    # System dependencies for PyQt5
    qt5.qtbase
    qt5.wrapQtAppsHook
    libGL
    libxkbcommon
    xorg.libX11
    xorg.libXrender
    xorg.libXext
    fontconfig
    freetype
    dbus

    # SSHFS for mounting
    sshfs

    # Build tools
    binutils
    patchelf
  ];

  # Set up Qt environment for running the app
  shellHook = ''
    export QT_QPA_PLATFORM_PLUGIN_PATH="${pkgs.qt5.qtbase.bin}/lib/qt-${pkgs.qt5.qtbase.version}/plugins/platforms"
    export QT_PLUGIN_PATH="${pkgs.qt5.qtbase.bin}/lib/qt-${pkgs.qt5.qtbase.version}/plugins"
    
    # Create venv with PyPI packages (avoids Nix Qt plugin path issues with PyInstaller)
    if [ ! -d .venv ]; then
      echo "Creating Python virtual environment..."
      python3 -m venv .venv
      source .venv/bin/activate
      pip install --upgrade pip
      pip install PyQt5 pyinstaller
      echo ""
      echo "Virtual environment created with PyQt5 and PyInstaller from PyPI"
    else
      source .venv/bin/activate
    fi
    
    echo ""
    echo "SSHFS GUI Development Environment"
    echo "=================================="
    echo ""
    echo "Available commands:"
    echo "  python3 sshfs_gui.py  - Run the application"
    echo "  ./build.sh            - Build standalone binary"
    echo ""
    echo "Dependencies:"
    echo "  Python: $(python3 --version)"
    echo "  PyQt5:  $(python3 -c 'from PyQt5.QtCore import QT_VERSION_STR; print(QT_VERSION_STR)' 2>/dev/null || echo 'installing...')"
    echo "  SSHFS:  $(sshfs --version 2>&1 | head -1)"
    echo ""
    echo "Note: PyQt5 and PyInstaller are installed from PyPI in .venv"
    echo "      to avoid NixOS Qt plugin path issues during build."
    echo ""
  '';

  # Prevent Qt from complaining about missing plugins
  QT_QPA_PLATFORM = "xcb";
  
  # Library paths for Qt
  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.qt5.qtbase
    pkgs.libGL
    pkgs.libxkbcommon
    pkgs.xorg.libX11
    pkgs.xorg.libXrender
    pkgs.xorg.libXext
    pkgs.fontconfig
    pkgs.freetype
    pkgs.dbus
  ];
}
