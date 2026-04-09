import os
import json
import sys
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.platform = "windows" if sys.platform == "win32" else "linux"
        self.config_path = Path(__file__).parent / "paths.json"
        self.paths = self._load_paths()

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
        # Resolve ~ for home
        path_str = os.path.expanduser(path_str)
        # Resolve %ENV% for windows
        if self.platform == "windows":
            path_str = os.path.expandvars(path_str)
        return Path(path_str)

    def get_steam_roots(self):
        roots = self.paths.get("steam_roots", [])
        return [self._resolve_path(r) for r in roots]

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

config_manager = ConfigManager()
