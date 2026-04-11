# This Python file uses the following encoding: utf-8
import sys
import json
import subprocess
import os
import ctypes
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, QAbstractListModel, Property, Signal, QModelIndex

from launch.manager import LaunchManager, InstanceModel
from geode.manager import GeodeManager
from launch.downloader import Downloader
from config.manager import config_manager
from startup.ownership import check_gd_ownership

class LauncherBridge(QObject):
    usernameChanged = Signal()
    downloadPathChanged = Signal()
    rememberMeChanged = Signal()
    
    configChanged = Signal()
    geodeStatusChanged = Signal(str)
    setupStatusChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self._instance_model = InstanceModel()
        self._launch_manager = LaunchManager(self._instance_model)
        self._geode_manager = GeodeManager(self._instance_model, self)
        self._downloader = Downloader()
          
        self._config_path = Path("config.json")
        self._username = ""
        self._remember_me = False
        self._download_path = str(config_manager.get_default_instances_dir().resolve())
        self._setup_status = "ready"
        self._load_config()

        # Initial detection
        self._launch_manager.detect_installations()
        
        # Check setup status on init
        self._setup_status = self.check_setup_status()
        self.setupStatusChanged.emit(self._setup_status)

    def _load_config(self):
        if self._config_path.exists():
            try:
                with open(self._config_path, "r") as f:
                    data = json.load(f)
                    self._username = data.get("username", "")
                    self._remember_me = data.get("remember_me", False)
                    self._download_path = data.get("download_path", self._download_path)
            except Exception:
                pass

    def _save_config(self):
        try:
            with open(self._config_path, "w") as f:
                json.dump({
                    "username": self._username,
                    "remember_me": self._remember_me,
                    "download_path": self._download_path
                }, f)
        except Exception:
            pass

    @Property(str, notify=usernameChanged)
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
        self.usernameChanged.emit()
        self._save_config()

    @Property(bool, notify=rememberMeChanged)
    def rememberMe(self):
        return self._remember_me

    @rememberMe.setter
    def rememberMe(self, value):
        self._remember_me = value
        self.rememberMeChanged.emit()
        self._save_config()

    @Property(str, notify=downloadPathChanged)
    def downloadPath(self):
        return self._download_path

    @downloadPath.setter
    def downloadPath(self, value):
        self._download_path = value
        self.downloadPathChanged.emit()
        self._save_config()

    @Property(str, notify=setupStatusChanged)
    def setupStatus(self):
        return self._setup_status

    @setupStatus.setter
    def setupStatus(self, value):
        self._setup_status = value
        self.setupStatusChanged.emit()

    @Slot(result=QAbstractListModel)
    def instanceModel(self):
        return self._instance_model

    @Slot()
    def detect_installations(self):
        self._launch_manager.detect_installations()

    def _is_steam_valid(self, index):
        if 0 <= index < self._instance_model.rowCount():
            instance = self._instance_model._instances[index]
            if instance.get("source") == "Local":
                return True
            ownership = instance.get("ownership", "Unknown")
            return ownership in ["Owned", "Family Shared"]
        return False

    @Slot(result=str)
    def check_setup_status(self):
        """
        Returns 'ready', 'needs_ownership', or 'needs_permissions'
        """
        ownership = check_gd_ownership()
        if ownership not in ["Owned", "Family Shared"]:
            self._setup_status = "needs_ownership"
            self.setupStatusChanged.emit(self._setup_status)
            return self._setup_status
        
        if sys.platform == "win32":
            official_path = self._launch_manager.get_official_gd_path()
            if official_path and official_path.exists():
                common_path = official_path.parent
                if not os.access(str(common_path), os.W_OK):
                    self._setup_status = "needs_permissions"
                    self.setupStatusChanged.emit(self._setup_status)
                    return self._setup_status
        
        # On non-Windows platforms, we assume permissions are fine (no UAC concept)
        self._setup_status = "ready"
        self.setupStatusChanged.emit(self._setup_status)
        return self._setup_status
        
    @Slot()
    def refresh_setup_status(self):
        """Re-checks setup status and updates UI."""
        self._setup_status = self.check_setup_status()

    @Slot()
    def request_folder_permissions(self):
        """Runs icacls as Administrator to grant folder permissions on Windows."""
        if sys.platform != "win32":
            return

        official_path = self._launch_manager.get_official_gd_path()
        if not official_path:
            return

        common_path = official_path.parent
        
        import getpass
        current_user = getpass.getuser()
        
        cmd = f'icacls "{common_path}" /grant {current_user}:(OI)(CI)F /T'
        
        try:
            ctypes.shell32.ShellExecuteW(None, "runas", "cmd.exe", f"/c {cmd}", None, 1)
        except Exception as e:
            print(f"Failed to request permissions: {e}")

    @Slot()
    def open_steam_store(self):
        """Opens the Geometry Dash Steam store page."""
        url = "https://store.steampowered.com/app/322170/Geometry_Dash/"
        if sys.platform == "win32":
            os.startfile(url)
        else:
            open_cmd = config_manager.get_open_cmd()
            subprocess.Popen([open_cmd, url])

    @Slot(int)
    def launch_instance(self, index):
        if not self._is_steam_valid(index):
            print(f"Blocking launch for instance {index}: Invalid ownership")
            return
        self._launch_manager.launch(index, None)

    @Slot(int, str)
    def launch_instance_with_profile(self, index, profile):
        if not self._is_steam_valid(index):
            print(f"Blocking launch for instance {index}: Invalid ownership")
            return
        self._launch_manager.launch(index, profile)

    @Slot(int)
    @Slot(int, str)
    def create_geode_profile(self, index, name="New Profile"):
        if not self._is_steam_valid(index):
            return
        self._geode_manager.create_profile(index, name)

    @Slot(int, str)
    def delete_geode_profile(self, index, profile_name):
        if not self._is_steam_valid(index):
            return
        self._geode_manager.delete_profile(index, profile_name)

    @Slot(int, str, str)
    def rename_geode_profile(self, index, old_name, new_name):
        if not self._is_steam_valid(index):
            return
        self._geode_manager.rename_profile(index, old_name, new_name)

    @Slot(int, bool)
    def toggle_geode(self, index, enabled):
        if not self._is_steam_valid(index):
            return
        self._geode_manager.toggle_geode(index, enabled)

    @Slot(int)
    def install_geode(self, index):
        if not self._is_steam_valid(index):
            return
        self._geode_manager.install_geode(index)

    @Slot(int, result="QVariantList")
    def get_profiles(self, index):
        if 0 <= index < self._instance_model.rowCount():
            return self._instance_model._instances[index]["profiles"]
        return []

    @Slot(int, result=bool)
    def get_geode_enabled(self, index):
        if 0 <= index < self._instance_model.rowCount():
            return self._instance_model._instances[index]["geode_enabled"]
        return False

    @Slot(int, result=str)
    def get_ownership(self, index):
        if 0 <= index < self._instance_model.rowCount():
            return self._instance_model._instances[index].get("ownership", "Unknown")
        return "Unknown"
    
    @Slot(int, result=str)
    def get_source(self, index):
        if 0 <= index < self._instance_model.rowCount():
            return self._instance_model._instances[index].get("source", "Steam")
        return "Steam"

    @Slot(int, result=str)
    def get_instance_path(self, index):
        if 0 <= index < self._instance_model.rowCount():
            return self._instance_model._instances[index].get("path", "")
        return ""

    @Slot(str, str, str, str, str, str, str)
    def start_download(self, username, password, name, app_id, depot_id, manifest_id, code):
        dest = Path(self._download_path) / name
        self._downloader.download_version(
            username, password, app_id, depot_id, manifest_id, dest, 
            code if code else None
        )

    @Slot(int)
    def open_instance_folder(self, index):
        if 0 <= index < self._instance_model.rowCount():
            path = self._instance_model._instances[index].get("path", "")
            if path:
                if sys.platform == "win32":
                    os.startfile(path)
                else:
                    open_cmd = config_manager.get_open_cmd()
                    subprocess.Popen([open_cmd, path])

    @Slot(int)
    def delete_instance(self, index):
        if 0 <= index < self._instance_model.rowCount():
            instance = self._instance_model._instances[index]
            if instance.get("source") == "Local":
                path = Path(instance.get("path", ""))
                if path.exists():
                    import shutil
                    try:
                        shutil.rmtree(path)
                        self._instance_model.beginRemoveRows(QModelIndex(), index, index)
                        self._instance_model._instances.pop(index)
                        self._instance_model.endRemoveRows()
                    except Exception as e:
                        print(f"Failed to delete instance: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Ensure palette follows system theme (dark/light mode)
    from PySide6.QtGui import QPalette
    app.setPalette(QPalette())
    
    # Set Fusion style with system theme for Qt6
    from PySide6.QtQuickControls2 import QQuickStyle
    QQuickStyle.setStyle("Fusion")
    
    engine = QQmlApplicationEngine()
    base_path = str(config_manager.base_path.resolve())
    engine.addImportPath(base_path)
    engine.addImportPath(os.path.join(base_path, "ui"))
    engine.addImportPath(os.path.join(base_path, "ui/dialogs"))
    engine.addImportPath(os.path.join(base_path, "ui/components"))
    
    bridge = LauncherBridge()
    engine.rootContext().setContextProperty("launcher", bridge)
    engine.rootContext().setContextProperty("downloader", bridge._downloader)
        
    qml_file = config_manager.get_qml_path("main.qml")
    engine.load(qml_file)
    
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
