import os
import shutil
import sys
import subprocess
from pathlib import Path
from config.manager import config_manager

GEODE_DIR = "geode"
PROFILES_DIR = "profiles"
BACKUP_SUFFIX = ".default"
SYMLINK_DIRS = ["mods", "config", "resources", "saved"]

GD_APP_ID = "322170"


def _create_junction(source: Path, target: Path) -> bool:
    """Create a Windows junction. Returns True on success."""
    if sys.platform != "win32":
        return False
    try:
        subprocess.run([
            'powershell', '-Command',
            f'Start-Process cmd -ArgumentList "/c mklink /J \\"{target}\\" \\"{source}\\"" -Verb RunAs'
        ], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Failed to create junction: {e}")
        return False


def _remove_junction(path: Path) -> bool:
    """Remove a Windows junction. Returns True on success."""
    if sys.platform != "win32":
        return False
    try:
        subprocess.run([
            'powershell', '-Command',
            f'Start-Process cmd -ArgumentList "/c rmdir \\"{path}\\"" -Verb RunAs'
        ], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Failed to remove junction: {e}")
        return False


def get_geode_data_dir(gd_path: Path):
    gd_path = Path(gd_path)
    
    # Check if geode is in the game directory (common for manual installs)
    gd_geode = gd_path / GEODE_DIR
    if gd_geode.exists() and gd_geode.is_dir():
        return gd_geode
    
    # Check for Steam/Proton compatdata path (Linux only)
    if sys.platform != "win32":
        steam_path = gd_path
        while steam_path.parent != steam_path:
            if str(steam_path.name) == "steamapps":
                compat = steam_path.parent / "compatdata" / GD_APP_ID / "pfx" / "drive_c" / "ProgramData" / "Geode"
                if compat.exists():
                    return compat
                break
            steam_path = steam_path.parent
    
    # Check configured/common paths
    common_paths = config_manager.get_geode_data_dirs()
    for p in common_paths:
        if p.exists():
            return p
    
    return None

def get_geode_version(gd_path: Path) -> str:
    """Get the installed Geode version from the version file."""
    geode_dir = get_geode_data_dir(gd_path)
    if not geode_dir:
        return "Not installed"
    
    version_file = geode_dir / "version"
    if version_file.exists():
        try:
            return version_file.read_text().strip()
        except Exception as e:
            print(f"Error reading Geode version: {e}")
    
    return "Unknown"

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

        if not src.exists():
            src.mkdir(parents=True, exist_ok=True)

        is_junction = False
        if sys.platform == "win32":
            try:
                output = subprocess.check_output(['cmd', '/c', 'dir', str(dst.parent)], text=True)
                is_junction = f"<JUNCTION>     {dst.name}" in output
            except:
                pass

        if dst.is_symlink() or is_junction:
            if is_junction:
                _remove_junction(dst)
            else:
                dst.unlink()
        elif dst.exists():
            backup = Path(str(dst) + BACKUP_SUFFIX)
            if not backup.exists():
                print(f"Backing up {dst} to {backup}")
                shutil.move(str(dst), str(backup))
            else:
                if dst.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()

        if sys.platform == "win32":
            if not _create_junction(src.resolve(), dst):
                print(f"Failed to create junction for {dst}")
        else:
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

        is_junction = False
        if sys.platform == "win32":
            try:
                output = subprocess.check_output(['cmd', '/c', 'dir', str(dst.parent)], text=True)
                is_junction = f"<JUNCTION>     {dst.name}" in output
            except:
                pass

        if dst.is_symlink() or is_junction:
            if is_junction:
                _remove_junction(dst)
            else:
                dst.unlink()

        backup = Path(str(dst) + BACKUP_SUFFIX)
        if backup.exists() and not dst.exists():
            print(f"Restoring {dst} from {backup}")
            shutil.move(str(backup), str(dst))
        
        if not dst.exists():
            dst.mkdir(parents=True, exist_ok=True)
            
    return True
