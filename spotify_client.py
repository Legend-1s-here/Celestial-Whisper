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

    def __init__(self, client_id: str = "", client_secret: str = "", redirect_uri: str = ""):
        super().__init__()
        self.client_id = client_id.strip()
        self.client_secret = client_secret.strip()
        self.redirect_uri = redirect_uri.strip() or "http://127.0.0.1:8888/callback"
        
        self.running = True
        self.use_native_windows = True  # Default to rock-solid Windows media monitor
        self.powershell_proc: Optional[subprocess.Popen] = None
        
        self.current_track_id: Optional[str] = None
        self.is_playing = False
        self.progress_sec = 0.0
        self.last_sync_time = 0.0
        self.duration_sec = 0.0
        
        # Spotipy instance if configured
        self.sp = None

    def update_credentials(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id.strip()
        self.client_secret = client_secret.strip()
        self.redirect_uri = redirect_uri.strip() or "http://127.0.0.1:8888/callback"
        
        if self.client_id and self.client_secret:
            try:
                import spotipy
                from spotipy.oauth2 import SpotifyOAuth
                cache_path = Path(__file__).parent / ".spotify_token_cache"
                auth_manager = SpotifyOAuth(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    redirect_uri=self.redirect_uri,
                    scope="user-read-playback-state user-read-currently-playing",
                    open_browser=True,
                    cache_path=str(cache_path)
                )
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                # Test API call
                self.sp.current_user_playing_track()
                self.use_native_windows = False
                self.status_message.emit("Connected via Spotify Web API.")
            except Exception as e:
                err_str = str(e)
                if "403" in err_str or "Active premium subscription" in err_str:
                    self.status_message.emit("Spotify API requires Premium (403). Using Windows Media Mode (Free).")
                else:
                    self.status_message.emit(f"Spotify API notice: {e}. Using Windows Media Mode.")
                self.use_native_windows = True
                self.sp = None
        else:
            self.use_native_windows = True
            self.sp = None

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
        except Exception as e:
            self.status_message.emit(f"Failed to start Windows media monitor: {e}")

    def run(self):
        # If user provided API keys, check if they work
        if self.client_id and self.client_secret:
            self.update_credentials(self.client_id, self.client_secret, self.redirect_uri)
        else:
            self.use_native_windows = True

        self._start_powershell_monitor()
        last_interp_time = time.time()

        while self.running:
            now = time.time()

            # Mode 1: Windows Native Media Monitor (100% Free, NO Premium required!)
            if self.use_native_windows:
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

            # Mode 2: Spotify Web API (if user has active Spotify Premium and configured keys)
            else:
                try:
                    playback = self.sp.current_user_playing_track()
                    if playback and playback.get("item"):
                        item = playback["item"]
                        track_id = item.get("id") or item.get("name")
                        title = item.get("name", "Unknown")
                        artists = ", ".join(a["name"] for a in item.get("artists", []))
                        duration_ms = item.get("duration_ms", 0)
                        progress_ms = playback.get("progress_ms", 0)
                        self.is_playing = playback.get("is_playing", False)

                        self.progress_sec = progress_ms / 1000.0
                        self.last_sync_time = now

                        if track_id != self.current_track_id:
                            self.current_track_id = track_id
                            self.track_changed.emit({
                                "track_id": track_id,
                                "title": title,
                                "artist": artists,
                                "duration_ms": duration_ms,
                                "is_playing": self.is_playing,
                                "progress_sec": self.progress_sec
                            })
                    else:
                        if self.current_track_id is not None:
                            self.current_track_id = None
                            self.is_playing = False
                            self.track_changed.emit({
                                "track_id": None,
                                "title": "",
                                "artist": "",
                                "duration_ms": 0,
                                "is_playing": False,
                                "progress_sec": 0
                            })
                except Exception as e:
                    err_str = str(e)
                    if "403" in err_str or "Active premium subscription" in err_str:
                        # Auto fallback to Windows Media Mode
                        self.status_message.emit("Switching to Windows Media Mode (Free, no Premium required).")
                        self.use_native_windows = True
                        self._start_powershell_monitor()
                    time.sleep(1.0)

            time.sleep(0.05)

    def stop(self):
        self.running = False
        if self.powershell_proc:
            try:
                self.powershell_proc.terminate()
                self.powershell_proc.wait(timeout=1)
            except Exception:
                pass
        self.wait(1000)
