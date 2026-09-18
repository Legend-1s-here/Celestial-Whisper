import sys
import re
import os
import json
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Tuple, Optional
import syncedlyrics

try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate
    HAS_INDIC = True
except Exception:
    HAS_INDIC = False

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def safe_log(msg: str):
    try:
        print(msg)
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

def fallback_to_hinglish(text: str) -> str:
    """Rule-based fallback from Devanagari Hindi to Hinglish."""
    if not HAS_INDIC:
        return text
    if not any(0x0900 <= ord(c) <= 0x097F for c in text):
        return text
    try:
        res = transliterate(text, sanscript.DEVANAGARI, sanscript.IAST)
        replacements = {
            'ā': 'aa', 'ī': 'ee', 'ū': 'oo', 'ṛ': 'ri', 'ṝ': 'ri',
            'ṃ': 'n', 'ḥ': 'h', 'ṅ': 'n', 'ñ': 'n', 'ṇ': 'n',
            'ṭ': 't', 'ḍ': 'd', 'ṣ': 'sh', 'ś': 'sh', 'ḷ': 'l'
        }
        for k, v in replacements.items():
            res = res.replace(k, v)
            res = res.replace(k.upper(), v.capitalize())
        return res
    except Exception:
        return text

def romanize_lyrics(lines: List[str]) -> List[str]:
    """
    Converts Hindi Devanagari / foreign text into clean English alphabet (e.g. 'Yaad aati nahi').
    Uses Google's dt=rm romanizer with local fallback.
    """
    if not lines:
        return []
    non_ascii = sum(1 for line in lines for c in line if ord(c) > 127)
    if non_ascii == 0:
        return lines

    non_empty = [(i, l) for i, l in enumerate(lines) if l.strip()]
    if not non_empty:
        return lines

    indices, texts = zip(*non_empty)
    combined = "\n".join(texts)
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=rm&q=" + urllib.parse.quote(combined)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            rom_text = ""
            for item in data[0]:
                if len(item) > 3 and item[3]:
                    rom_text = item[3]
                    break
            if rom_text:
                rom_lines = rom_text.splitlines()
                result = list(lines)
                for idx, r in zip(indices, rom_lines):
                    result[idx] = r.strip()
                return result
    except Exception as e:
        safe_log(f"[LyricsFetcher] Romanization error: {e}, falling back to local Hinglish rules")

    # Local fallback
    return [fallback_to_hinglish(l) for l in lines]

def translate_lines_to_english(lines: List[str]) -> List[str]:
    """Translates lyrics to English meaning."""
    if not lines:
        return []
    non_ascii = sum(1 for line in lines for c in line if ord(c) > 127)
    if non_ascii == 0:
        return lines

    non_empty = [(i, l) for i, l in enumerate(lines) if l.strip()]
    if not non_empty:
        return lines

    indices, texts = zip(*non_empty)
    combined = "\n".join(texts)
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q=" + urllib.parse.quote(combined)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            translated_text = "".join([part[0] for part in data[0] if part and part[0]])
            trans_lines = translated_text.splitlines()

        result = list(lines)
        for idx, t in zip(indices, trans_lines):
            result[idx] = t.strip()
        return result
    except Exception as e:
        safe_log(f"[LyricsFetcher] Translation error: {e}")
        return lines

class LyricsManager:
    def __init__(self, language_mode: str = "romanized"):
        self.current_lyrics: List[LyricLine] = []
        self.original_lyrics: List[LyricLine] = []
        self.romanized_lyrics: List[LyricLine] = []
        self.translated_lyrics: List[LyricLine] = []
        
        self.current_song_key: str = ""
        self.is_synced: bool = False
        self.raw_text: str = ""
        self.language_mode = language_mode  # "romanized" (default Hinglish), "translation", "original"

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

    def set_language_mode(self, mode: str):
        self.language_mode = mode
        self._apply_current_language()

    def _apply_current_language(self):
        if not self.original_lyrics:
            return

        if self.language_mode == "romanized" and self.romanized_lyrics:
            self.current_lyrics = self.romanized_lyrics
        elif self.language_mode == "translation" and self.translated_lyrics:
            self.current_lyrics = self.translated_lyrics
        else:
            self.current_lyrics = self.original_lyrics

    def fetch_lyrics(self, artist: str, title: str, language_mode: str = None) -> bool:
        if not title:
            return False

        if language_mode:
            self.language_mode = language_mode

        song_key = f"{artist.lower().strip()} - {title.lower().strip()}"
        if song_key == self.current_song_key and self.original_lyrics:
            self._apply_current_language()
            return True

        self.current_song_key = song_key
        self.current_lyrics = []
        self.original_lyrics = []
        self.romanized_lyrics = []
        self.translated_lyrics = []
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
                        self.original_lyrics = self.parse_lrc(self.raw_text)
                        
                        if "romanized_lrc" in data:
                            self.romanized_lyrics = self.parse_lrc(data["romanized_lrc"])
                        if "translated_lrc" in data:
                            self.translated_lyrics = self.parse_lrc(data["translated_lrc"])

                        self._process_language_variants(cache_file, data)
                        self._apply_current_language()
                        safe_log(f"[LyricsFetcher] Loaded from cache: {title} ({self.language_mode})")
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
        queries.append(title)

        lrc = None
        for q in queries:
            safe_log(f"[LyricsFetcher] Searching synced lyrics for: {q}")
            try:
                lrc = syncedlyrics.search(q, synced_only=True)
                if lrc:
                    break
            except Exception as e:
                safe_log(f"[LyricsFetcher] Search error on '{q}': {e}")

        if lrc:
            parsed = self.parse_lrc(lrc)
            if parsed:
                self.original_lyrics = parsed
                self.is_synced = True
                self.raw_text = lrc
                cache_data = {"is_synced": True, "lrc": lrc, "title": title, "artist": artist}
                self._process_language_variants(cache_file, cache_data)
                self._apply_current_language()
                return True

        return False

    def _process_language_variants(self, cache_file: Path, cache_data: dict):
        if not self.original_lyrics:
            return

        has_foreign = any(ord(c) > 127 for line in self.original_lyrics for c in line.text)
        if not has_foreign:
            return

        # 1. Generate Romanized English letters (Hinglish: 'Yaad aati nahi')
        if not self.romanized_lyrics:
            texts = [l.text for l in self.original_lyrics]
            rom_texts = romanize_lyrics(texts)
            if rom_texts and len(rom_texts) == len(self.original_lyrics):
                self.romanized_lyrics = [
                    LyricLine(self.original_lyrics[i].time_sec, rom_texts[i])
                    for i in range(len(self.original_lyrics))
                ]
                rom_lrc = "\n".join([f"[{int(l.time_sec//60):02d}:{l.time_sec%60:05.2f}] {l.text}" for l in self.romanized_lyrics])
                cache_data["romanized_lrc"] = rom_lrc

        # 2. Generate English translation meaning
        if not self.translated_lyrics:
            texts = [l.text for l in self.original_lyrics]
            trans_texts = translate_lines_to_english(texts)
            if trans_texts and len(trans_texts) == len(self.original_lyrics):
                self.translated_lyrics = [
                    LyricLine(self.original_lyrics[i].time_sec, trans_texts[i])
                    for i in range(len(self.original_lyrics))
                ]
                trans_lrc = "\n".join([f"[{int(l.time_sec//60):02d}:{l.time_sec%60:05.2f}] {l.text}" for l in self.translated_lyrics])
                cache_data["translated_lrc"] = trans_lrc

        # Save to cache
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

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
