import os
import shutil
from pathlib import Path

GEODE_DIR = "geode"
PROFILES_DIR = "profiles"
BACKUP_SUFFIX = ".default"
SYMLINK_DIRS = ["mods", "config", "resources", "saved"]

GD_APP_ID = "322170"

def get_geode_data_dir(gd_path: Path):
    gd_path = Path(gd_path)
    
    # Check if geode is in the game directory (common for manual installs)
    gd_geode = gd_path / GEODE_DIR
    if gd_geode.exists() and gd_geode.is_dir():
        return gd_geode
    
    # Check for Steam/Proton compatdata path
    steam_path = gd_path
    while steam_path.parent != steam_path:
        if str(steam_path.name) == "steamapps":
            compat = steam_path.parent / "compatdata" / GD_APP_ID / "pfx" / "drive_c" / "ProgramData" / "Geode"
            if compat.exists():
                return compat
            break
        steam_path = steam_path.parent
    
    # Check common Linux paths
    local_share = Path.home() / ".local/share/Geode"
    if local_share.exists():
        return local_share
    
    config_geode = Path.home() / ".config/geode"
    if config_geode.exists():
        return config_geode
    
    return None

def activate_profile(gd_path: str, profile_name: str):
    geode_dir = get_geode_data_dir(Path(gd_path))
    if not geode_dir:
        print(f"Geode directory not found for {gd_path}")
        return False

    profiles_root = geode_dir / PROFILES_DIR
    profile_path = profiles_root / profile_name
    
    if not profile_path.exists():
        profile_path.mkdir(parents=True, exist_ok=True)

    for d in SYMLINK_DIRS:
        src = profile_path / d
        dst = geode_dir / d

        # Ensure source directory exists in the profile
        if not src.exists():
            src.mkdir(parents=True, exist_ok=True)

        # Handle destination
        if dst.is_symlink():
            dst.unlink()
        elif dst.exists():
            # Backup existing 'default' data if it hasn't been backed up yet
            backup = Path(str(dst) + BACKUP_SUFFIX)
            if not backup.exists():
                print(f"Backing up {dst} to {backup}")
                shutil.move(str(dst), str(backup))
            else:
                # If backup exists, we can safely remove the current one to make room for symlink
                if dst.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()

        # Create symlink
        try:
            dst.symlink_to(src.resolve(), target_is_directory=True)
            print(f"Symlinked {dst} -> {src}")
        except Exception as e:
            print(f"Failed to symlink {dst}: {e}")

    return True

def deactivate_profile(gd_path: str):
    geode_dir = get_geode_data_dir(Path(gd_path))
    if not geode_dir:
        return False

    for d in SYMLINK_DIRS:
        dst = geode_dir / d
        if dst.is_symlink():
            dst.unlink()

        # Restore from backup if it exists
        backup = Path(str(dst) + BACKUP_SUFFIX)
        if backup.exists() and not dst.exists():
            print(f"Restoring {dst} from {backup}")
            shutil.move(str(backup), str(dst))
        
        # If no backup and still doesn't exist, create an empty one
        if not dst.exists():
            dst.mkdir(parents=True, exist_ok=True)
            
    return True
