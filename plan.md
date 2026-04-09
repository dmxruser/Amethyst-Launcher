# Amethyst Launcher - Development Plan

## Current Progress
- **DRM & EULA Compliance**: Refactored `launch/manager.py` to use the **Symlink/Junction Swap** method.
  - No longer bypasses Steam DRM.
  - Every instance is launched through the official Steam Client (`steam://rungameid/322170`).
  - Automatic restoration of the official folder once the game process exits.
- **Windows Robustness**:
  - Switched from standard Symlinks to **Directory Junctions** (`mklink /J`) to improve stability and avoid specialized "Developer Mode" requirements.
  - Added **`steam_appid.txt`** (App ID 322170) creation in instance folders as a secondary safeguard for the Steam API.
- **Backend Setup**:
  - `main.py` now includes `check_setup_status()`, `request_folder_permissions()`, and `open_steam_store()`.
  - Refined the **`icacls`** strategy to target the `steamapps/common` folder, allowing the launcher to rename and swap the Geometry Dash directory without requiring UAC every time.

## Permissions Strategy (The "Mod Manager" Approach)
1. **No Global Admin**: The launcher is compiled with `uac_admin=False` to start instantly as a standard user.
2. **One-Time Authorization**: During first-time setup or when creating the first instance, the user is prompted to "Authorize Amethyst."
3. **The Trick**: The launcher runs `icacls "%COMMON_PATH%" /grant %username%:(OI)(CI)F /T` via a single elevated command.
4. **Permanent Access**: Once granted, the launcher can freely manage the GD folder for swapping/linking without ever needing UAC again.

## Next Steps
- **UI Integration**:
  - Hook `check_setup_status()` into the `DownloadDialog.qml` and the Instance Creation flow.
  - Design a simple "Setup Wizard" or "Permission Prompt" in QML for when `needs_permissions` or `needs_ownership` is returned.
- **Validation**:
  - Test the `icacls` scope on a live Windows environment to ensure renaming `Geometry Dash` to `Geometry Dash.original` works flawlessly under the new permissions.
- **Download Automation**:
  - Refine the moving/management of files after `download_depot` finishes in the Steam Client.

**Status**: Ready to resume UI implementation tomorrow.
