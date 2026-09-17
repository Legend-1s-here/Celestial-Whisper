import sys
import os
import threading
from pathlib import Path

# Set Windows App User Model ID so taskbar shows custom icon
if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CelestialWhisper.LyricsOverlay.1.0")
    except Exception:
        pass

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon

from config import load_config, save_config
from lyrics_fetcher import LyricsManager
from spotify_client import SpotifyWorker
from overlay import FloatingLyricsOverlay
from settings_ui import SettingsDialog
from tray import SystemTray

ICON_PATH = Path(__file__).parent / "app.ico"

SAMPLE_LYRICS = [
    (0.0, "♪ Music Intro ♪"),
    (3.0, "There's a fire starting in my heart"),
    (7.0, "Reaching a fever pitch, it's bringing me out the dark"),
    (12.0, "Finally I can see you crystal clear"),
    (16.0, "Go ahead and sell me out and I'll lay your ship bare"),
    (21.0, "See how I'll leave with every piece of you"),
    (25.0, "Don't underestimate the things that I will do"),
    (30.0, "♪ End of Preview ♪")
]

class ApplicationController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        if ICON_PATH.exists():
            self.app.setWindowIcon(QIcon(str(ICON_PATH)))

        self.config = load_config()
        self.lyrics_manager = LyricsManager()
        self.overlay = FloatingLyricsOverlay(self.config)
        self.overlay.show()

        # Settings dialog
        self.settings_dialog = None

        # Preview timer
        self.is_preview_mode = False
        self.preview_start_time = 0.0
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self._update_preview)

        # Windows Media worker thread (no login or API keys needed!)
        self.spotify_worker = SpotifyWorker()
        self.spotify_worker.track_changed.connect(self._on_track_changed)
        self.spotify_worker.position_updated.connect(self._on_position_updated)
        self.spotify_worker.status_message.connect(self._on_status_message)
        self.spotify_worker.start()

        # System tray
        self.tray = SystemTray()
        self.tray.toggle_overlay.connect(self._toggle_overlay)
        self.tray.open_settings.connect(self.show_settings)
        self.tray.position_changed.connect(self._set_position)
        self.tray.context_mode_changed.connect(self._set_context_mode)
        self.tray.test_lyrics.connect(self.start_preview_mode)
        self.tray.action_exit.triggered.connect(self.close_app)
        self.tray.show()

        # Overlay signals
        self.overlay.open_settings_requested.connect(self.show_settings)
        self.overlay.position_mode_changed.connect(self._on_overlay_position_changed)

    def _toggle_overlay(self):
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show()

    def _set_position(self, mode: str):
        self.overlay.set_position_mode(mode)
        self.config["position"] = mode
        save_config(self.config)

    def _set_context_mode(self, mode: str):
        self.config["context_mode"] = mode
        save_config(self.config)
        self.overlay.apply_config(self.config)

    def _on_overlay_position_changed(self, mode: str):
        self.config["position"] = mode
        save_config(self.config)

    def show_settings(self):
        if not self.settings_dialog or not self.settings_dialog.isVisible():
            self.settings_dialog = SettingsDialog(self.config)
            if ICON_PATH.exists():
                self.settings_dialog.setWindowIcon(QIcon(str(ICON_PATH)))
            self.settings_dialog.settings_saved.connect(self._on_settings_saved)
            self.settings_dialog.test_lyrics_requested.connect(self.start_preview_mode)
            self.settings_dialog.show()
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()

    def _on_settings_saved(self, new_config: dict):
        self.config = new_config
        save_config(self.config)
        self.overlay.apply_config(self.config)

    def start_preview_mode(self):
        import time
        self.is_preview_mode = True
        self.preview_start_time = time.time()
        self.overlay.show()
        self.overlay.showStatus("▶ Sample Preview: Adele — Rolling in the Deep", "Testing floating lyrics...")
        self.preview_timer.start(100)

    def _update_preview(self):
        import time
        elapsed = time.time() - self.preview_start_time
        if elapsed > 32.0:
            self.preview_timer.stop()
            self.is_preview_mode = False
            self.overlay.showStatus("🎶 Ready for Spotify", "Play any song on Spotify")
            return

        active_idx = -1
        for i, (t, _) in enumerate(SAMPLE_LYRICS):
            if t <= elapsed:
                active_idx = i
            else:
                break

        if active_idx != -1:
            curr = SAMPLE_LYRICS[active_idx][1]
            prev = SAMPLE_LYRICS[active_idx - 1][1] if active_idx > 0 else ""
            nxt = SAMPLE_LYRICS[active_idx + 1][1] if (active_idx + 1 < len(SAMPLE_LYRICS)) else ""
            self.overlay.setLyrics(prev, curr, nxt)

    def _on_track_changed(self, track_info: dict):
        if self.is_preview_mode:
            return

        title = track_info.get("title", "").strip()
        artist = track_info.get("artist", "").strip()
        is_playing = track_info.get("is_playing", False)

        if not title:
            self.overlay.showStatus("🎶 Spotify Idle", "Play a song on Spotify to see floating lyrics")
            return

        self.overlay.showStatus(f"🎵 {title}", f"by {artist}" if artist else "")

        def fetch_task():
            found = self.lyrics_manager.fetch_lyrics(artist, title)
            if not found:
                self.overlay.showStatus(f"🎵 {title}", "(No synchronized lyrics found)")

        threading.Thread(target=fetch_task, daemon=True).start()

    def _on_position_updated(self, progress_sec: float):
        if self.is_preview_mode:
            return

        if self.lyrics_manager.is_synced and self.lyrics_manager.current_lyrics:
            prev, curr, nxt, idx = self.lyrics_manager.get_lines_at(progress_sec)
            self.overlay.setLyrics(prev, curr, nxt)

    def _on_status_message(self, msg: str):
        print(f"[MediaWorker] {msg}")

    def close_app(self):
        self.spotify_worker.stop()
        self.app.quit()

    def run(self):
        return self.app.exec()

if __name__ == "__main__":
    controller = ApplicationController()
    sys.exit(controller.run())
