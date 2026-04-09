import subprocess
import os
import threading
import time
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot


class Downloader(QObject):
    progress = Signal(float)
    finished = Signal(bool, str)
    output_received = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._stop_requested = False

    def download_version(self, username, password, app_id, depot_id, manifest_id, destination_path, code=None):
        """
        Uses the Steam client console (steam://console/) to download depot content.
        """
        def run():
            try:
                depot_dir = Path(os.path.expanduser("~/Steam/steamapps/content"))
                app_depot_dir = depot_dir / f"app_{app_id}" / f"depot_{depot_id}"
                app_depot_dir.mkdir(parents=True, exist_ok=True)

                self.output_received.emit("Opening Steam console...")
                
                console_url = f"steam://open/console"
                subprocess.Popen(
                    ["xdg-open", console_url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(2)

                download_depot_cmd = f"download_depot {app_id} {depot_id}"
                if manifest_id:
                    download_depot_cmd += f" {manifest_id}"

                self.output_received.emit(f"Command: {download_depot_cmd}")
                self.output_received.emit("Note: Run this command in the Steam console (steam://open/console)")
                self.output_received.emit(f"Expected download location: {app_depot_dir}")

                self.output_received.emit("Sending command to Steam console...")
                
                subprocess.Popen(
                    ["xdg-open", f"steam://console/{download_depot_cmd}"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                self.output_received.emit("Download command sent to Steam client.")
                self.output_received.emit("Please monitor the download in your Steam client.")
                self.output_received.emit(f"Files will be downloaded to: {app_depot_dir}")

                self.finished.emit(True, f"Download command sent. Check Steam client for progress. Files will be in: {app_depot_dir}")

            except Exception as e:
                self.finished.emit(False, str(e))

        self._stop_requested = False
        threading.Thread(target=run, daemon=True).start()

    @Slot()
    def stop(self):
        self._stop_requested = True