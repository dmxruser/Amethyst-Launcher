import os
import json
import sys
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.platform = "windows" if sys.platform == "win32" else "linux"
        
        if hasattr(sys, "_MEIPASS"):
            self.base_path = Path(sys._MEIPASS)
        else:
            self.base_path = Path(__file__).parent.parent
            
        self.config_path = self.base_path / "config" / "paths.json"
        self.paths = self._load_paths()

    def get_qml_path(self, filename="main.qml"):
        return self.base_path / filename

    def _load_paths(self):
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                return data.get(self.platform, {})
        except Exception as e:
            print(f"Error loading paths.json: {e}")
            return {}

    def _resolve_path(self, path_str):
        if not path_str:
            return None
        if self.platform == "windows":
            path_str = os.path.expandvars(path_str)
        path_str = os.path.expanduser(path_str)
        resolved = Path(path_str)
        if not resolved.is_absolute():
            resolved = self.base_path / resolved
        return resolved

    def get_steam_roots(self):
        roots = self.paths.get("steam_roots", [])
        resolved = [self._resolve_path(r) for r in roots]
        
        if self.platform == "windows":
            try:
                import winreg
                for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                    for subkey in [
                        r"SOFTWARE\Valve\Steam",
                        r"SOFTWARE\WOW6432Node\Valve\Steam"
                    ]:
                        try:
                            key = winreg.OpenKey(hive, subkey)
                            install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                            if install_path:
                                path = Path(install_path)
                                if path not in resolved:
                                    resolved.append(path)
                            winreg.CloseKey(key)
                        except FileNotFoundError:
                            pass
            except Exception:
                pass
        
        return resolved

    def get_geode_data_dirs(self):
        dirs = self.paths.get("geode_data_dirs", [])
        return [self._resolve_path(d) for d in dirs]

    def get_default_instances_dir(self):
        return self._resolve_path(self.paths.get("default_instances_dir", "instances"))

    def get_steam_cmd(self):
        return self.paths.get("steam_cmd", "steam")

    def get_open_cmd(self):
        return self.paths.get("open_cmd", "xdg-open" if self.platform == "linux" else "explorer")

    def get_wine_cmd(self):
        return self.paths.get("wine_cmd", "")

    def get_default_save_dir(self):
        if self.platform == "windows":
            return Path(os.path.expandvars("%LOCALAPPDATA%")) / "GeometryDash"
        elif self.platform == "linux":
            return Path(os.path.expanduser("~/.local/share/GeometryDash"))
        return None

config_manager = ConfigManager()
