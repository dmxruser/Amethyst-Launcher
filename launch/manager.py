import subprocess
import re
import os
import shutil
from pathlib import Path
from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex

from geode.loadprofile import activate_profile, deactivate_profile, get_geode_data_dir
from startup.ownership import check_gd_ownership

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

    def detect_installations(self):
        self.model.clear()
        
        # 1. Scan Steam installations
        steam_root_paths = [
            Path.home() / ".steam/steam",
            Path.home() / ".steam/debian-installation",
            Path.home() / ".local/share/Steam",
            Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam",
            Path.home() / ".var/app/com.valvesoftware.Steam/.steam/steam",
        ]
        
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
        instances_dir = Path("instances")
        if instances_dir.exists() and instances_dir.is_dir():
            for item in instances_dir.iterdir():
                if item.is_dir():
                    # Check if it contains GeometryDash.exe
                    exe_path = item / "GeometryDash.exe"
                    if exe_path.exists():
                        self._add_with_geode_check(item.name, item, source="Local")

    def _get_geode_data_dir(self, gd_path: Path):
        gd_geode = gd_path / "geode"
        if gd_geode.exists() and gd_geode.is_dir():
            return gd_geode
        steam_path = gd_path
        while steam_path.parent != steam_path:
            if str(steam_path.name) == "steamapps":
                compat = steam_path.parent / "compatdata" / GD_APP_ID / "pfx" / "drive_c" / "ProgramData" / "Geode"
                if compat.exists():
                    return compat
                break
            steam_path = steam_path.parent
        local_share = Path.home() / ".local/share/Geode"
        if local_share.exists():
            return local_share
        config_geode = Path.home() / ".config/geode"
        if config_geode.exists():
            return config_geode
        return None

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
        instance = self.model._instances[index]
        gd_path = Path(instance["path"])
        source = instance.get("source", "Steam")

        if instance.get("geode_enabled") and profile and profile != "Default":
            activate_profile(str(gd_path), profile)
        else:
            deactivate_profile(str(gd_path))

        if source == "Steam":
            # Try to launch steam directly with applaunch parameter first
            steam_path = shutil.which("steam")
            if steam_path:
                subprocess.Popen([steam_path, "-applaunch", GD_APP_ID])
            else:
                # Fallback to xdg-open with steam:// protocol
                subprocess.Popen(["xdg-open", f"steam://rungameid/{GD_APP_ID}"])
        else:
            # Local launch
            exe_path = gd_path / "GeometryDash.exe"
            # We probably need wine/proton to run it on linux
            # For now let's try just running it, but usually wine is needed.
            # Assuming user has wine installed or we use a specific runner.
            env = os.environ.copy()
            # If steam_appid.txt exists, it helps
            subprocess.Popen(["wine", str(exe_path)], cwd=str(gd_path), env=env)
