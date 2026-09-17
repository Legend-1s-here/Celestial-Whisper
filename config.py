import json
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

DEFAULT_CONFIG = {
    "position": "bottom",  # "bottom" or "top"
    "font_size": 24,
    "text_color": "#FFB7C5",
    "glow_color": "#000000",
    "context_mode": "next_only",  # "both", "next_only", "none"
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

    # Ensure ample dimensions
    if config.get("window_width", 0) < 1200:
        config["window_width"] = 1400
    if config.get("window_height", 0) < 220:
        config["window_height"] = 240

    if "context_mode" not in config:
        config["context_mode"] = "next_only"

    return config

def save_config(config: dict) -> None:
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")
