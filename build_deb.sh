#!/bin/bash

# Build the binary first
echo "Building binary with PyInstaller..."
pyinstaller amethyst.spec --noconfirm

# Create DEB structure
echo "Creating DEB structure..."
BUILD_DIR="build/deb"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR/usr/bin
mkdir -p $BUILD_DIR/usr/share/amethyst-launcher
mkdir -p $BUILD_DIR/usr/share/applications
mkdir -p $BUILD_DIR/DEBIAN

# Copy files
echo "Copying files..."
cp -r dist/AmethystLauncher/* $BUILD_DIR/usr/share/amethyst-launcher/

# Create a launcher script in /usr/bin
echo "Creating launcher script..."
cat <<EOT > $BUILD_DIR/usr/bin/amethyst-launcher
#!/bin/sh
/usr/share/amethyst-launcher/amethyst-launcher "\$@"
EOT
chmod +x $BUILD_DIR/usr/bin/amethyst-launcher

# Create Desktop Entry
echo "Creating desktop entry..."
cat <<EOT > $BUILD_DIR/usr/share/applications/amethyst-launcher.desktop
[Desktop Entry]
Name=Amethyst Launcher
Exec=amethyst-launcher
Icon=/usr/share/amethyst-launcher/ui/icon.png
Type=Application
Categories=Game;
EOT

# Create Control file
echo "Creating control file..."
cat <<EOT > $BUILD_DIR/DEBIAN/control
Package: amethyst-launcher
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Your Name <you@example.com>
Description: A cross-platform Geometry Dash launcher with Geode support.
EOT

# Build it
echo "Building DEB package..."
dpkg-deb --build $BUILD_DIR amethyst-launcher_1.0.0_amd64.deb

echo "Done! Package created: amethyst-launcher_1.0.0_amd64.deb"
