import json
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

DEFAULT_CONFIG = {
    "spotify_client_id": "",
    "spotify_client_secret": "",
    "spotify_redirect_uri": "http://127.0.0.1:8888/callback",
    "position": "bottom",  # "bottom" or "top"
    "font_size": 26,
    "text_color": "#FFFFFF",
    "glow_color": "#000000",
    "context_mode": "next_only",  # "both", "next_only", "none"
    "show_context": True,
    "window_width": 1400,
    "window_height": 240,
    "lock_position": False
}

def load_config() -> dict:
    config = DEFAULT_CONFIG.copy()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                config.update(saved)
        except Exception as e:
            print(f"Error loading config: {e}")

    # Upgrade window width to at least 1400 to prevent text cutoffs
    if config.get("window_width", 0) < 1400:
        config["window_width"] = 1400
    if config.get("window_height", 0) < 240:
        config["window_height"] = 240

    # Handle migration from boolean show_context if context_mode not set
    if "context_mode" not in config:
        config["context_mode"] = "both" if config.get("show_context", True) else "none"

    return config

def save_config(config: dict) -> None:
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")
