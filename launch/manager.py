import subprocess
import re
import os
import shutil
import sys
from pathlib import Path
from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex

from geode.loadprofile import activate_profile, deactivate_profile, get_geode_data_dir
from startup.ownership import check_gd_ownership
from config.manager import config_manager

GD_APP_ID = "322170"

GEODE_WINDOWS_MARKERS = {"geode.dll", "xinput1_4.dll"}
GEODE_LINUX_MARKERS = {"geode", "libgeode.so", "Geode.dll"}
GEODE_PROFILE_DIR = "profiles"

class InstanceModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    PathRole = Qt.UserRole + 2
    GeodeRole = Qt.UserRole + 3
    ProfilesRole = Qt.UserRole + 4
    OwnershipRole = Qt.UserRole + 5
    SourceRole = Qt.UserRole + 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self._instances = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._instances)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._instances)):
            return None
        instance = self._instances[index.row()]
        if role == self.NameRole:
            return instance.get("name")
        elif role == self.PathRole:
            return instance.get("path")
        elif role == self.GeodeRole:
            return instance.get("geode_enabled", False)
        elif role == self.ProfilesRole:
            return instance.get("profiles", [])
        elif role == self.OwnershipRole:
            return instance.get("ownership", "Unknown")
        elif role == self.SourceRole:
            return instance.get("source", "Steam")
        return None

    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.PathRole: b"path",
            self.GeodeRole: b"geode_enabled",
            self.ProfilesRole: b"profiles",
            self.OwnershipRole: b"ownership",
            self.SourceRole: b"source"
        }

    def add_instance(self, name, path, geode_enabled=False, profiles=None, ownership="Unknown", source="Steam"):
        if profiles is None:
            profiles = []
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._instances.append({
            "name": name, 
            "path": str(path), 
            "geode_enabled": geode_enabled,
            "profiles": list(profiles),
            "ownership": ownership,
            "source": source
        })
        self.endInsertRows()

    def update_profiles(self, index):
        idx = self.index(index, 0)
        self.dataChanged.emit(idx, idx, [self.ProfilesRole])

    def update_geode_enabled(self, index):
        idx = self.index(index, 0)
        self.dataChanged.emit(idx, idx, [self.GeodeRole])

    def clear(self):
        self.beginResetModel()
        self._instances = []
        self.endResetModel()

class LaunchManager:
    def __init__(self, model: InstanceModel):
        self.model = model

    def get_official_gd_path(self):
        """Finds the actual Steam installation folder for Geometry Dash."""
        steam_root_paths = config_manager.get_steam_roots()
        processed_libraries = set()

        # 1. Check libraryfolders.vdf
        for root in steam_root_paths:
            vdf_path = root / "steamapps/libraryfolders.vdf"
            if vdf_path.exists():
                try:
                    with open(vdf_path, "r") as f:
                        content = f.read()
                    paths = re.findall(r'"path"\s*"([^"]+)"', content)
                    for path_str in paths:
                        lib_path = Path(path_str)
                        gd_path = lib_path / "steamapps/common/Geometry Dash"
                        if gd_path.exists():
                            return gd_path
                except Exception:
                    pass
        
        # 2. Check default steamapps/common
        for root in steam_root_paths:
            gd_path = root / "steamapps/common/Geometry Dash"
            if gd_path.exists():
                return gd_path
                
        return None

    def detect_installations(self):
        self.model.clear()
        
        # 1. Scan Steam installations
        steam_root_paths = config_manager.get_steam_roots()
        
        found_any = False
        processed_libraries = set()

        for root in steam_root_paths:
            vdf_path = root / "steamapps/libraryfolders.vdf"
            if vdf_path.exists():
                if self._parse_vdf(vdf_path, processed_libraries):
                    found_any = True
        
        if not found_any:
            for root in steam_root_paths:
                gd_path = root / "steamapps/common/Geometry Dash"
                if gd_path.exists() and str(gd_path) not in processed_libraries:
                    self._add_with_geode_check("Default Steam", gd_path, source="Steam")
                    processed_libraries.add(str(gd_path))

        # 2. Scan Local installations (Minecraft-style)
        instances_dir = config_manager.get_default_instances_dir()
        if instances_dir.exists() and instances_dir.is_dir():
            for item in instances_dir.iterdir():
                if item.is_dir():
                    # Check if it contains GeometryDash.exe
                    exe_path = item / "GeometryDash.exe"
                    if exe_path.exists():
                        self._add_with_geode_check(item.name, item, source="Local")

    def _get_geode_data_dir(self, gd_path: Path):
        return get_geode_data_dir(gd_path)

    def _scan_geode_profiles(self, geode_data_dir: Path):
        profiles = ["Default"]
        profile_dir = geode_data_dir / GEODE_PROFILE_DIR
        
        if profile_dir.exists() and profile_dir.is_dir():
            found_profiles = [d.name for d in profile_dir.iterdir() if d.is_dir()]
            for p in sorted(found_profiles):
                if p != "Default":
                    profiles.append(p)
        
        return profiles

    def _add_with_geode_check(self, name, path: Path, source="Steam"):
        geode_present = False
        try:
            files = [f.lower() for f in os.listdir(path)]
            all_markers = GEODE_WINDOWS_MARKERS | GEODE_LINUX_MARKERS
            if any(m.lower() in files for m in all_markers):
                geode_present = True
        except Exception:
            pass
        
        profiles = []
        if geode_present:
            geode_data_dir = self._get_geode_data_dir(path)
            if geode_data_dir:
                profiles = self._scan_geode_profiles(geode_data_dir)
            else:
                profiles = ["Default"]
            
        ownership = "Unknown"
        if source == "Steam":
            ownership = check_gd_ownership()
        else:
            ownership = "N/A (Local)"

        self.model.add_instance(name, path, geode_enabled=geode_present, profiles=profiles, ownership=ownership, source=source)

    def _parse_vdf(self, vdf_path, processed_libraries):
        found = False
        try:
            with open(vdf_path, "r") as f:
                content = f.read()
            
            paths = re.findall(r'"path"\s*"([^"]+)"', content)
            for path_str in paths:
                lib_path = Path(path_str)
                gd_path = lib_path / "steamapps/common/Geometry Dash"
                if gd_path.exists() and str(gd_path) not in processed_libraries:
                    self._add_with_geode_check("Default Steam", gd_path, source="Steam")
                    processed_libraries.add(str(gd_path))
                    found = True
        except Exception as e:
            print(f"Error parsing VDF {vdf_path}: {e}")
        return found

    def launch(self, index, profile=None):
        import threading
        import time

        instance = self.model._instances[index]
        gd_path = Path(instance["path"])
        source = instance.get("source", "Steam")

        if instance.get("geode_enabled") and profile and profile != "Default":
            activate_profile(str(gd_path), profile)
        else:
            deactivate_profile(str(gd_path))

        def monitor_and_restore(official_path: Path, original_backup: Path):
            """Monitors for the game process and restores the official folder when it exits."""
            try:
                # Wait for process to start (up to 30s)
                found = False
                for _ in range(60):
                    if self._is_game_running():
                        found = True
                        break
                    time.sleep(0.5)
                
                if found:
                    # Wait for process to exit
                    while self._is_game_running():
                        time.sleep(1)
                else:
                    print("Game process never detected. Restoring anyway.")
            finally:
                # Cleanup link/junction and restore
                if official_path.exists() or (sys.platform == "win32" and self._is_junction(official_path)):
                    if sys.platform == "win32":
                        # For junctions on Windows, rmdir is the safe way to remove the link without deleting content
                        try:
                            subprocess.run(['cmd', '/c', 'rmdir', str(official_path)], check=True)
                        except:
                            if official_path.is_symlink(): os.unlink(official_path)
                    else:
                        os.unlink(official_path)
                
                if original_backup.exists():
                    original_backup.rename(official_path)
                print("Restored official Geometry Dash installation.")

        if source == "Steam":
            # Direct Steam launch
            self._trigger_steam_launch()
        else:
            # Local launch via Swap-and-Steam
            official_path = self.get_official_gd_path()
            if not official_path:
                print("Error: Could not find official Steam installation of Geometry Dash.")
                return

            if official_path.resolve() == gd_path.resolve():
                self._trigger_steam_launch()
                return

            try:
                # 0. Ensure steam_appid.txt exists in the local instance (Legit secondary DRM safeguard)
                appid_file = gd_path / "steam_appid.txt"
                if not appid_file.exists():
                    with open(appid_file, "w") as f:
                        f.write(GD_APP_ID)

                # 1. Backup official
                original_backup = official_path.parent / (official_path.name + ".original")
                if not original_backup.exists():
                    official_path.rename(original_backup)
                else:
                    # Backup already exists, official_path might already be a link or missing
                    if official_path.exists():
                        # Something is wrong, let's remove the mystery file/link to make room
                        if sys.platform == "win32" and self._is_junction(official_path):
                            subprocess.run(['cmd', '/c', 'rmdir', str(official_path)], check=True)
                        else:
                            if official_path.is_dir() and not official_path.is_symlink():
                                # This is a real dir, we shouldn't delete it! 
                                # Renaming to a timestamped backup instead.
                                official_path.rename(official_path.parent / f"{official_path.name}.{int(time.time())}.bak")
                            else:
                                os.unlink(official_path)

                # 2. Create Link (Symlink on Linux, Junction on Windows)
                if sys.platform == "win32":
                    # mklink /J works without admin rights and is very stable for this
                    subprocess.run(['cmd', '/c', 'mklink', '/J', str(official_path), str(gd_path)], check=True)
                else:
                    os.symlink(gd_path, official_path)

                # 3. Launch via Steam
                self._trigger_steam_launch()

                # 4. Start restoration monitor
                threading.Thread(target=monitor_and_restore, args=(official_path, original_backup), daemon=True).start()

            except Exception as e:
                print(f"Failed to perform symlink swap: {e}")
                # Emergency restore if possible
                if 'original_backup' in locals() and original_backup.exists() and not official_path.exists():
                    try:
                        original_backup.rename(official_path)
                    except: pass

    def _trigger_steam_launch(self):
        steam_cmd = config_manager.get_steam_cmd()
        steam_path = shutil.which(steam_cmd)
        if steam_path:
            subprocess.Popen([steam_path, "-applaunch", GD_APP_ID])
        else:
            open_cmd = config_manager.get_open_cmd()
            if sys.platform == "win32":
                os.startfile(f"steam://rungameid/{GD_APP_ID}")
            else:
                subprocess.Popen([open_cmd, f"steam://rungameid/{GD_APP_ID}"])

    def _is_game_running(self):
        """Checks if GeometryDash.exe is currently running."""
        try:
            if sys.platform == "win32":
                output = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq GeometryDash.exe'], text=True)
                return "GeometryDash.exe" in output
            else:
                output = subprocess.check_output(['pgrep', '-f', 'GeometryDash'], text=True)
                return len(output.strip()) > 0
        except:
            return False

    def _is_junction(self, path: Path):
        """Specifically checks if a path is a Windows Directory Junction."""
        if sys.platform != "win32": return False
        try:
            # Junctions are 'd' type in dir but have <JUNCTION> in output
            output = subprocess.check_output(['cmd', '/c', 'dir', str(path.parent)], text=True)
            return f"<JUNCTION>     {path.name}" in output
        except:
            return False
