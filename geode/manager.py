import os
import shutil
import json
import zipfile
import threading
import sys
import urllib.request
from pathlib import Path
from PySide6.QtCore import QObject, Slot
from geode.loadprofile import get_geode_data_dir, PROFILES_DIR

# Just a lot of code for making profiles
class GeodeManager:
    def __init__(self, model, bridge=None):
        self.model = model
        self.bridge = bridge

    def _get_geode_profile_dir(self, instance_index):
        if not (0 <= instance_index < self.model.rowCount()):
            return None
        instance = self.model._instances[instance_index]
        gd_path = Path(instance["path"])
        geode_data_dir = get_geode_data_dir(gd_path)
        if geode_data_dir:
            return geode_data_dir / PROFILES_DIR
        return None
    
    def create_profile(self, instance_index, name="New Profile"):
        #Checks for if it exists
        if 0 <= instance_index < self.model.rowCount():
            instance = self.model._instances[instance_index]
            if name not in instance["profiles"]:
                profile_dir = self._get_geode_profile_dir(instance_index)
                if profile_dir:
                    profile_path = profile_dir / name
                    if not profile_path.exists():
                        profile_path.mkdir(parents=True, exist_ok=True)
                instance["profiles"].append(name)
                idx = self.model.index(instance_index, 0)
                self.model.dataChanged.emit(idx, idx, [self.model.ProfilesRole])
                print(f"Created Geode profile '{name}' for instance {instance_index}")

    def delete_profile(self, instance_index, profile_name):
        #Ditto except in reverse
        if 0 <= instance_index < self.model.rowCount():
            instance = self.model._instances[instance_index]
            if profile_name in instance["profiles"]:
                profile_dir = self._get_geode_profile_dir(instance_index)
                if profile_dir:
                    profile_path = profile_dir / profile_name
                    if profile_path.exists() and profile_path.is_dir():
                        shutil.rmtree(profile_path)
                instance["profiles"].remove(profile_name)
                idx = self.model.index(instance_index, 0)
                self.model.dataChanged.emit(idx, idx, [self.model.ProfilesRole])
                print(f"Deleted Geode profile '{profile_name}' for instance {instance_index}")

    def rename_profile(self, instance_index, old_name, new_name):
        #Ditto except its renamed
        if 0 <= instance_index < self.model.rowCount():
            instance = self.model._instances[instance_index]
            if old_name in instance["profiles"]:
                profile_dir = self._get_geode_profile_dir(instance_index)
                if profile_dir:
                    old_path = profile_dir / old_name
                    new_path = profile_dir / new_name
                    if old_path.exists() and old_path.is_dir():
                        old_path.rename(new_path)
                idx = instance["profiles"].index(old_name)
                instance["profiles"][idx] = new_name
                model_idx = self.model.index(instance_index, 0)
                self.model.dataChanged.emit(model_idx, model_idx, [self.model.ProfilesRole])
                print(f"Renamed Geode profile '{old_name}' to '{new_name}'")

    def toggle_geode(self, instance_index, enabled):
        if not (0 <= instance_index < self.model.rowCount()):
            return
        
        instance = self.model._instances[instance_index]
        gd_path = Path(instance["path"])
        
        # We need the markers from launch/manager.py really, but we can redefine for local use
        markers = ["geode.dll", "xinput1_4.dll", "geode", "libgeode.so", "Geode.dll"]
        
        found_any = False
        if enabled:
            # Look for .disabled files and enable them
            for f in os.listdir(gd_path):
                if f.lower().endswith(".disabled"):
                    base = f[:-9] # remove .disabled
                    if base.lower() in markers:
                        os.rename(gd_path / f, gd_path / base)
                        found_any = True
        else:
            # Look for active markers and disable them
            for f in os.listdir(gd_path):
                if f.lower() in markers:
                    os.rename(gd_path / f, gd_path / (f + ".disabled"))
                    found_any = True

        instance["geode_enabled"] = enabled
        idx = self.model.index(instance_index, 0)
        self.model.dataChanged.emit(idx, idx, [self.model.GeodeRole])
        print(f"Toggled Geode for instance {instance_index}: {enabled}")

    def install_geode(self, instance_index):
        if not (0 <= instance_index < self.model.rowCount()):
            return
        
        def run():
            try:
                instance = self.model._instances[instance_index]
                gd_path = Path(instance["path"])
                
                def set_status(msg):
                    if self.bridge:
                        self.bridge.geodeStatusChanged.emit(msg)

                set_status("Fetching latest Geode release...")
                api_url = "https://api.github.com/repos/geode-sdk/geode/releases/latest"
                # Use a specific user agent as GitHub API requires it
                headers = {"User-Agent": "Amethyst-Launcher"}
                req = urllib.request.Request(api_url, headers=headers)
                
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
                
                # Filter for correct platform
                platform_suffix = "win.zip" if sys.platform == "win32" else "linux.zip"
                
                download_url = None
                for asset in data.get("assets", []):
                    if asset["name"].endswith(platform_suffix):
                        download_url = asset["browser_download_url"]
                        break
                
                if not download_url:
                    set_status(f"Error: Could not find Geode release for {sys.platform}")
                    return

                set_status(f"Downloading Geode...")
                zip_path = gd_path / "geode_temp.zip"
                
                # urllib.request.urlretrieve doesn't support headers easily, but we don't need them for the download url usually
                urllib.request.urlretrieve(download_url, zip_path)
                
                set_status("Extracting Geode...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(gd_path)
                
                os.remove(zip_path)
                set_status("Geode installed successfully!")
                
                # Update model
                instance["geode_enabled"] = True
                
                # Re-scan for profiles as installing might create/reveal them
                geode_data_dir = get_geode_data_dir(gd_path)
                if geode_data_dir:
                    # In a real scenario we'd call the launch manager's scan but for now just ensure Default
                    if not instance["profiles"]:
                        instance["profiles"] = ["Default"]

                idx = self.model.index(instance_index, 0)
                self.model.dataChanged.emit(idx, idx, [self.model.GeodeRole, self.model.ProfilesRole])
                
                # Clear status after a bit
                import time
                time.sleep(3)
                set_status("")

            except Exception as e:
                set_status(f"Error: {str(e)}")
                print(f"Failed to install Geode: {e}")

        threading.Thread(target=run, daemon=True).start()
