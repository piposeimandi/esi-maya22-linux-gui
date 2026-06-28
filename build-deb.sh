#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PACKAGE="maya22-gui"
VERSION="1.0.0-1"
BUILD_DIR="build"
DEB_DIR="${BUILD_DIR}/${PACKAGE}_${VERSION}"

echo "==> Cleaning previous build..."
rm -rf "$BUILD_DIR"

echo "==> Creating package structure..."
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/share/${PACKAGE}"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/48x48/apps"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/128x128/apps"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/256x256/apps"

echo "==> Copying files..."
install -D -m 755 maya22-gui.py   "$DEB_DIR/usr/share/${PACKAGE}/maya22-gui.py"
install -D -m 755 maya22-control  "$DEB_DIR/usr/share/${PACKAGE}/maya22-control"
install -D -m 644 images/maya22-icon.svg      "$DEB_DIR/usr/share/icons/hicolor/scalable/apps/maya22-gui.svg"
install -D -m 644 images/maya22-icon.png      "$DEB_DIR/usr/share/icons/hicolor/256x256/apps/maya22-gui.png"
install -D -m 644 images/maya22-icon-48.png   "$DEB_DIR/usr/share/icons/hicolor/48x48/apps/maya22-gui.png"
install -D -m 644 images/maya22-icon-128.png  "$DEB_DIR/usr/share/icons/hicolor/128x128/apps/maya22-gui.png"
install -D -m 644 debian/maya22-gui.desktop   "$DEB_DIR/usr/share/applications/maya22-gui.desktop"

echo "==> Creating control file..."
cat > "$DEB_DIR/DEBIAN/control" <<EOF
Package: ${PACKAGE}
Version: ${VERSION}
Section: sound
Priority: optional
Architecture: all
Maintainer: Adrian Seimandi <bajosega@gmail.com>
Depends: python3 (>= 3.8), python3-pil, python3-pil.imagetk, python3-tk
Recommends: gir1.2-ayatanaappindicator3-0.1
Description: GUI controller for ESI Maya22 USB audio interface
 Graphical interface to control the ESI Maya22 USB audio interface
 via the maya22-control binary. Adjust input/output volumes,
 select input channels, and toggle monitoring/headphones.
EOF

echo "==> Building .deb package..."
dpkg-deb --root-owner-group --build "$DEB_DIR" > /dev/null

echo ""
echo "✅ Package created: ${BUILD_DIR}/${PACKAGE}_${VERSION}.deb"
echo ""
echo "Install with:"
echo "  sudo apt install ./${BUILD_DIR}/${PACKAGE}_${VERSION}.deb"
echo ""
echo "Then install customtkinter (not available in Debian repos):"
echo "  pip install customtkinter"
