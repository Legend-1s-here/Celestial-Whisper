import sys
import os
import time
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QThread

MEDIA_SCRIPT_PATH = Path(__file__).parent / "media_monitor.ps1"

class SpotifyWorker(QThread):
    track_changed = pyqtSignal(dict)       # Emits {title, artist, duration_ms, is_playing, progress_sec, track_id}
    position_updated = pyqtSignal(float)   # Emits progress_sec for smooth sync
    status_message = pyqtSignal(str)       # Status updates

    def __init__(self):
        super().__init__()
        self.running = True
        self.powershell_proc: Optional[subprocess.Popen] = None
        
        self.current_track_id: Optional[str] = None
        self.is_playing = False
        self.progress_sec = 0.0
        self.last_sync_time = 0.0
        self.duration_sec = 0.0

    def _start_powershell_monitor(self):
        if self.powershell_proc and self.powershell_proc.poll() is None:
            return
        try:
            cmd = [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-File", str(MEDIA_SCRIPT_PATH)
            ]
            self.powershell_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )
            self.status_message.emit("Native Windows media monitor active.")
        except Exception as e:
            self.status_message.emit(f"Failed to start Windows media monitor: {e}")

    def run(self):
        self._start_powershell_monitor()

        while self.running:
            now = time.time()

            if not self.powershell_proc or self.powershell_proc.poll() is not None:
                self._start_powershell_monitor()
                time.sleep(0.5)
                continue

            try:
                line = self.powershell_proc.stdout.readline()
                if line:
                    line = line.strip()
                    if line.startswith("{") and line.endswith("}"):
                        data = json.loads(line)
                        title = data.get("title", "").strip()
                        artist = data.get("artist", "").strip()
                        status = data.get("status", "")
                        pos_sec = float(data.get("position_sec", 0.0))
                        dur_sec = float(data.get("duration_sec", 0.0))

                        is_playing = (status == "Playing")
                        track_id = f"{artist} - {title}" if title else None

                        self.is_playing = is_playing
                        self.progress_sec = pos_sec
                        self.duration_sec = dur_sec
                        self.last_sync_time = now

                        if track_id != self.current_track_id:
                            self.current_track_id = track_id
                            self.track_changed.emit({
                                "track_id": track_id,
                                "title": title,
                                "artist": artist,
                                "duration_ms": int(dur_sec * 1000),
                                "is_playing": is_playing,
                                "progress_sec": pos_sec
                            })

                        self.position_updated.emit(pos_sec)
            except Exception:
                pass

            time.sleep(0.04)

    def stop(self):
        self.running = False
        if self.powershell_proc:
            try:
                self.powershell_proc.terminate()
                self.powershell_proc.wait(timeout=1)
            except Exception:
                pass
        self.wait(1000)
