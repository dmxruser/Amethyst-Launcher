; installer.iss
[Setup]
AppName=Amethyst Launcher
AppVersion=1.0.0
DefaultDirName={autopf}\Amethyst Launcher
DefaultGroupName=Amethyst Launcher
OutputDir=.
OutputBaseFilename=AmethystLauncher-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\AmethystLauncher\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Amethyst Launcher"; Filename: "{app}\amethyst-launcher.exe"
Name: "{autodesktop}\Amethyst Launcher"; Filename: "{app}\amethyst-launcher.exe"

[Run]
Filename: "{app}\amethyst-launcher.exe"; Description: "Launch Amethyst Launcher"; Flags: nowait postinstall skipifsilent
