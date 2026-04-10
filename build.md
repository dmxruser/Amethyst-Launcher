# Building Amethyst Launcher on Windows

## Prerequisites

- Python 3.9+
- [Inno Setup](https://jrsoftware.org/isinfo.php) (for creating the installer)

## Step 1: Install Dependencies

```powershell
pip install -r requirements.txt
```

## Step 2: Build the Application

Use PySide6 project tools to build:

```powershell
pyside6-project
```

Or build manually with PyInstaller/cx_Freeze (not included in this project).

## Step 3: Create the Installer

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Open `installer.iss` in Inno Setup Compiler
3. Compile the script to generate `AmethystLauncher-Setup.exe`

The installer will be output to the project root directory.

## Notes

- This is a PySide6/Qt Quick application
- The app is a Geometry Dash launcher (uses PySide6, Geode mod manager)
- Output goes to `dist\AmethystLauncher\` directory
