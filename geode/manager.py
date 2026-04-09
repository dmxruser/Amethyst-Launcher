import os
import shutil
from pathlib import Path
from PySide6.QtCore import QObject, Slot
from geode.loadprofile import get_geode_data_dir, PROFILES_DIR

# Just a lot of code for making profiles
class GeodeManager:
    def __init__(self, model):
        self.model = model

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
