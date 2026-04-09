import re
import os
from pathlib import Path
from config.manager import config_manager

GD_APP_ID = "322170"

def get_steam_root():
    """Tries to find the Steam installation directory."""
    paths = config_manager.get_steam_roots()
    for p in paths:
        if p.exists():
            return p
    return None

def get_current_steam_user(steam_root: Path):
    """Gets the SteamID64 of the most recently logged-in user."""
    vdf_path = steam_root / "config/loginusers.vdf"
    if not vdf_path.exists():
        return None
        
    try:
        with open(vdf_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Find all user blocks
        # SteamID64s are 17-digit strings starting with 765
        user_blocks = re.findall(r'"(\d{17})"\s*\{([^}]+)\}', content, re.DOTALL)
        
        for steamid, data in user_blocks:
            if r'"MostRecent"\s*"1"'.lower() in re.sub(r'\s+', ' ', data).lower():
                return steamid
                
        if user_blocks:
            return user_blocks[0][0]
    except Exception as e:
        print(f"Error reading loginusers.vdf: {e}")
        
    return None

def check_gd_ownership():
    """Checks if Geometry Dash is owned or family shared."""
    steam_root = get_steam_root()
    if not steam_root:
        return "Unknown (Steam not found)"
        
    current_user = get_current_steam_user(steam_root)
    if not current_user:
        return "Unknown (User not found)"
        
    manifest_name = f"appmanifest_{GD_APP_ID}.acf"
    manifest_path = steam_root / "steamapps" / manifest_name
    
    if not manifest_path.exists():
        library_vdf = steam_root / "steamapps/libraryfolders.vdf"
        if library_vdf.exists():
            try:
                with open(library_vdf, "r") as f:
                    content = f.read()
                paths = re.findall(r'"path"\s*"([^"]+)"', content)
                for p in paths:
                    potential_path = Path(p) / "steamapps" / manifest_name
                    if potential_path.exists():
                        manifest_path = potential_path
                        break
            except Exception:
                pass
                
    if not manifest_path.exists():
        return "Unknown (Manifest not found)"
        
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        match = re.search(r'"LastOwner"\s*"(\d+)"', content)
        if match:
            last_owner = match.group(1)
            if last_owner == current_user:
                return "Owned"
            else:
                return "Family Shared"
    except Exception as e:
        print(f"Error reading manifest: {e}")
        
    return "Unknown"

if __name__ == "__main__":
    print(f"GD Ownership: {check_gd_ownership()}")
