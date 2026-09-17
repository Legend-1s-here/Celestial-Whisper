import sys
import re
import os
import json
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional
import syncedlyrics

# Ensure safe UTF-8 output on Windows
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def safe_log(msg: str):
    try:
        print(msg)
    except Exception:
        try:
            print(msg.encode("ascii", "replace").decode("ascii"))
        except Exception:
            pass

CACHE_DIR = Path(__file__).parent / ".lyrics_cache"
CACHE_DIR.mkdir(exist_ok=True)

class LyricLine:
    def __init__(self, time_sec: float, text: str):
        self.time_sec = time_sec
        self.text = text

    def __repr__(self):
        return f"[{self.time_sec:.2f}s] {self.text}"

class LyricsManager:
    def __init__(self):
        self.current_lyrics: List[LyricLine] = []
        self.current_song_key: str = ""
        self.is_synced: bool = False
        self.raw_text: str = ""

    def clean_search_term(self, text: str) -> str:
        text = re.sub(r"\(feat\.[^\)]*\)", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\[feat\.[^\]]*\]", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\(with[^\)]*\)", "", text, flags=re.IGNORECASE)
        text = re.sub(r"-\s*remaster(ed)?(\s*\d+)?", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\(remaster(ed)?(\s*\d+)?\)", "", text, flags=re.IGNORECASE)
        return " ".join(text.split())

    def parse_lrc(self, lrc_content: str) -> List[LyricLine]:
        lines = []
        pattern = re.compile(r"^\[(\d+):(\d+(?:\.\d+)?)\](.*)$")
        for raw_line in lrc_content.splitlines():
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            match = pattern.match(raw_line)
            if match:
                minutes = int(match.group(1))
                seconds = float(match.group(2))
                text = match.group(3).strip()
                time_sec = minutes * 60.0 + seconds
                lines.append(LyricLine(time_sec, text))
        lines.sort(key=lambda x: x.time_sec)
        return lines

    def _get_cache_file(self, artist: str, title: str) -> Path:
        key = f"{artist.lower().strip()}_{title.lower().strip()}"
        hash_str = hashlib.md5(key.encode("utf-8", "ignore")).hexdigest()
        return CACHE_DIR / f"{hash_str}.json"

    def fetch_lyrics(self, artist: str, title: str) -> bool:
        if not title:
            return False

        song_key = f"{artist.lower().strip()} - {title.lower().strip()}"
        if song_key == self.current_song_key and self.current_lyrics:
            return True

        self.current_song_key = song_key
        self.current_lyrics = []
        self.is_synced = False
        self.raw_text = ""

        # Check local cache
        cache_file = self._get_cache_file(artist, title)
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.is_synced = data.get("is_synced", False)
                    self.raw_text = data.get("lrc", "")
                    if self.is_synced and self.raw_text:
                        self.current_lyrics = self.parse_lrc(self.raw_text)
                        safe_log(f"[LyricsFetcher] Loaded from cache: {title}")
                        return True
            except Exception as e:
                safe_log(f"Cache read error: {e}")

        # Search synced lyrics
        queries = []
        if artist and artist != "Unknown":
            queries.append(f"{artist} {title}")
            clean_title = self.clean_search_term(title)
            if clean_title != title:
                queries.append(f"{artist} {clean_title}")
        queries.append(title)  # Search just title if artist query fails

        for q in queries:
            safe_log(f"[LyricsFetcher] Searching synced lyrics for: {q}")
            try:
                lrc = syncedlyrics.search(q, synced_only=True)
                if lrc:
                    parsed = self.parse_lrc(lrc)
                    if parsed:
                        self.current_lyrics = parsed
                        self.is_synced = True
                        self.raw_text = lrc
                        try:
                            with open(cache_file, "w", encoding="utf-8") as f:
                                json.dump({"is_synced": True, "lrc": lrc, "title": title, "artist": artist}, f, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                        return True
            except Exception as e:
                safe_log(f"[LyricsFetcher] Search error on query '{q}': {e}")

        # Fallback: Search plain lyrics
        for q in queries[:2]:
            try:
                plain = syncedlyrics.search(q, synced_only=False)
                if plain:
                    self.raw_text = plain
                    self.is_synced = False
                    try:
                        with open(cache_file, "w", encoding="utf-8") as f:
                            json.dump({"is_synced": False, "lrc": plain, "title": title, "artist": artist}, f, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                    return True
            except Exception:
                pass

        return False

    def get_lines_at(self, current_sec: float) -> Tuple[str, str, str, int]:
        if not self.current_lyrics:
            return ("", "", "", -1)

        active_idx = -1
        for i, line in enumerate(self.current_lyrics):
            if line.time_sec <= current_sec:
                active_idx = i
            else:
                break

        if active_idx == -1:
            first_text = self.current_lyrics[0].text if self.current_lyrics else ""
            return ("", "♪ ... ♪", first_text, -1)

        curr_text = self.current_lyrics[active_idx].text or "♪"
        prev_text = self.current_lyrics[active_idx - 1].text if active_idx > 0 else ""
        next_text = self.current_lyrics[active_idx + 1].text if (active_idx + 1 < len(self.current_lyrics)) else ""

        return (prev_text, curr_text, next_text, active_idx)
