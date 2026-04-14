import subprocess
import os
import shutil
import threading
import time
import sys
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot
from config.manager import config_manager


class Downloader(QObject):
    progress = Signal(float)
    finished = Signal(bool, str)
    output_received = Signal(str)
    instance_added = Signal(str)

    def __init__(self):
        super().__init__()
        self._stop_requested = False
        self._download_app_id = None
        self._download_depot_id = None
        self._download_dest = None

    def download_version(self, username, password, app_id, depot_id, manifest_id, destination_path, code=None):
        """
        Uses the Steam client console (steam://console/) to download depot content.
        """
        self._download_app_id = app_id
        self._download_depot_id = depot_id
        self._download_dest = Path(destination_path)

        def run():
            try:
                steam_root = None
                for root in config_manager.get_steam_roots():
                    if root.exists():
                        steam_root = root
                        break

                if not steam_root:
                    self.finished.emit(False, "Steam installation not found.")
                    return

                depot_dir = steam_root / "steamapps/content"
                app_depot_dir = depot_dir / f"app_{app_id}" / f"depot_{depot_id}"

                self.output_received.emit("Opening Steam console...")

                open_cmd = config_manager.get_open_cmd()
                console_url = f"steam://open/console"

                if sys.platform == "win32":
                    os.startfile(console_url)
                else:
                    subprocess.Popen(
                        [open_cmd, console_url],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                time.sleep(2)

                download_depot_cmd = f"download_depot {app_id} {depot_id}"
                if manifest_id:
                    download_depot_cmd += f" {manifest_id}"

                self.output_received.emit(f"Command: {download_depot_cmd}")
                self.output_received.emit(f"Expected download location: {app_depot_dir}")

                self.output_received.emit("Sending command to Steam client...")

                if sys.platform == "win32":
                    os.startfile(f"steam://console/{download_depot_cmd}")
                else:
                    subprocess.Popen(
                        [open_cmd, f"steam://console/{download_depot_cmd}"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )

                self.output_received.emit("Download command sent to Steam client.")
                self.output_received.emit("Waiting for download to complete...")

                self._wait_for_download(app_depot_dir, manifest_id, open_cmd)

            except Exception as e:
                self.finished.emit(False, str(e))

        self._stop_requested = False
        threading.Thread(target=run, daemon=True).start()

    def _wait_for_download(self, app_depot_dir: Path, manifest_id: str, open_cmd: str):
        max_wait = 600
        check_interval = 5
        
        test_mode = os.environ.get("AMETHYST_TEST_MODE", "")
        if test_mode == "1":
            max_wait = 10
            check_interval = 2
        elif test_mode == "fast":
            max_wait = 5
            check_interval = 1
        waited = 0

        while waited < max_wait:
            if app_depot_dir.exists():
                files = list(app_depot_dir.iterdir())
                if files:
                    self.output_received.emit(f"Download detected in {app_depot_dir}")
                    self._copy_files_to_instance(app_depot_dir, self._download_dest)
                    return
            time.sleep(check_interval)
            waited += check_interval

        self.output_received.emit("Timeout waiting for download. Please copy files manually.")
        self.finished.emit(True, "Download started. Copy files from Steam content folder to instance.")

    def _copy_files_to_instance(self, source_dir: Path, dest_dir: Path):
        import time

        def copy_with_retry(src, dst, max_retries=3):
            for attempt in range(max_retries):
                try:
                    shutil.copy2(src, dst)
                    return True
                except PermissionError:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                    else:
                        raise
            return False

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)

            total_files = sum(1 for _ in source_dir.rglob('*') if _.is_file())
            copied = 0
            failed = 0
            failed_files = []

            for item in source_dir.rglob('*'):
                if self._stop_requested:
                    self.output_received.emit("Copy stopped by user.")
                    return

                rel_path = item.relative_to(source_dir)
                dest_path = dest_dir / rel_path

                if item.is_file():
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        copy_with_retry(item, dest_path)
                        copied += 1
                        progress = (copied / total_files) * 100
                        self.progress.emit(progress)
                        self.output_received.emit(f"Copied {copied}/{total_files}: {rel_path.name}")
                    except Exception as e:
                        failed += 1
                        failed_files.append(str(rel_path))
                        self.output_received.emit(f"Failed to copy {rel_path.name}: {e}")
                elif item.is_dir():
                    dest_path.mkdir(parents=True, exist_ok=True)

            if failed > 0:
                self.output_received.emit(f"Completed with {failed} file(s) failed. Try closing Steam.")
                self.finished.emit(True, f"Installed to {dest_dir} ({copied}/{total_files} files, {failed} failed)")
            else:
                self.finished.emit(True, f"Successfully installed to {dest_dir}")
                self.output_received.emit(f"Installation complete! Files copied to: {dest_dir}")
            self.instance_added.emit(str(dest_dir))

        except Exception as e:
            self.finished.emit(False, f"Failed to copy files: {str(e)}")
            self.output_received.emit(f"Error copying files: {e}")

    @Slot()
    def stop(self):
        self._stop_requested = True