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

[Messages]
SetupAppRunningError=Close Geometry Dash first! You can't install while the game is running.

[Code]
var
  MsgIndex: Integer;
  GD_Messages: array of String;

function InitializeSetup(): Boolean;
begin
  GD_Messages := [
    'Falling decode wave... not!',
    'Sorry not mitigun',
    'Every level must have a spike',
    'Spamming at the start of ToE',
    'Drinking energy drinks for eon...',
    'AskReddit - Do you fall up or down? From KrazyMan50',
    'Buffing for no reason',
    'Checking steam... for a legit copy',
    'Make your own installing!',
    'Verifying Bloodbath, as cyclic',
    'Extending a main level like a content farm',
    '2.21 When?',
    'What is a geometry dash?',
    'Verifying Grief, as a 10 year old',
    'Removing skill issues, i think?',
    'You need a rest, thats how it goes in cataclysm right?',
    'Decrypting player data... 99% corrupted',
    'Loading demon list... getting dizzy',
    'Calibrating wave... failed, try again',
    'Spawning thousands of cubes...',
    'Summoning RobTop from the void...',
    'Searching for hidden coins in the installer...',
    'Adding more spikes to the level...',
    'Verifying you actually own the game...',
    'Downloading 0.1% of RobTop''s tears...'
  ];
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    MsgIndex := Random(Length(GD_Messages));
    WizardForm.StatusLabel2.Font.Style := [fsItalic];
    WizardForm.StatusLabel2.Caption := GD_Messages[MsgIndex];
  end;
end;

[Files]
Source: "dist\AmethystLauncher\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Amethyst Launcher"; Filename: "{app}\amethyst-launcher.exe"
Name: "{autodesktop}\Amethyst Launcher"; Filename: "{app}\amethyst-launcher.exe"

[Run]
Filename: "{app}\amethyst-launcher.exe"; Description: "Launch Amethyst Launcher"; Flags: nowait postinstall skipifsilent
