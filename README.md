<div align="center">

<img src="assets/celestial-whisper-banner.png" alt="Celestial Whisper — floating lyrics for Windows" width="100%" />

# Celestial Whisper

### A quiet lyric layer for loud worlds.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/UI-PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![Windows](https://img.shields.io/badge/Platform-Windows_10_%2F_11-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Spotify](https://img.shields.io/badge/Playback-Spotify-1ED760?style=for-the-badge&logo=spotify&logoColor=white)](https://spotify.com/)
[![License](https://img.shields.io/badge/License-MIT-F38BA8?style=for-the-badge)](./LICENSE)

<p>
  <strong>Read your music while you work, play, browse, or disappear into a film.</strong><br />
  Celestial Whisper is a lightweight, synchronized Spotify lyrics overlay that stays beautiful, readable, and out of the way.
</p>

</div>

---

## The idea

Music should not force you to choose between listening and looking.

Celestial Whisper turns synchronized lyrics into a frameless, translucent layer that floats above your desktop. It follows Spotify playback through Windows' native media session, keeps timing close to the song, and lets you tune the experience to your screen, language, game, and mood.

> **A small window into the song — never a window in the way.**

## See it in motion

The overlay is designed to remain readable over a game, editor, browser, or video without trapping the lyric inside an opaque panel. In Game Mode, clicks pass through to the application underneath.

<div align="center">

<img src="assets/floating-lyrics-example.png" alt="Celestial Whisper displaying synchronized lyrics over a game" width="100%" />

<sub>Example: keeping the lyric visible while continuing to play.</sub>

</div>

## What makes it different

<table>
<tr>
<td width="50%" valign="top">

### No Spotify API dance

Celestial Whisper reads playback through the Windows media session instead of requiring a Spotify developer application, OAuth flow, or Premium-only API setup. It is intended to work with Spotify Desktop and the Web Player on Windows.

</td>
<td width="50%" valign="top">

### A truly floating overlay

The lyric window is frameless, transparent, always-on-top, and rendered with high-contrast shadows. It can sit at the top of the display, rest in a cinema-style bottom position, or be dragged wherever it feels right.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### Three ways to understand a lyric

Keep the original script, switch to English meaning, or use English letters / Hinglish / Romaji for lyrics written in another script. The app caches fetched lyrics and language variants locally.

</td>
<td width="50%" valign="top">

### Built for the middle of a song

Use the tray icon for fast changes, preview sample lyrics before starting Spotify, toggle click-through gaming mode, or open the full Sakura-themed settings panel when you want finer control.

</td>
</tr>
</table>

## Feature map

### Overlay

- Frameless transparent lyric window with a subtle drop-shadow treatment.
- Always-on-top behavior with a Windows keep-alive for borderless and fullscreen-style games.
- Top-of-screen and bottom-center placement presets.
- Free drag-and-drop positioning, with an optional position lock.
- Three context modes: current + next, previous + current + next, or current only.
- Adjustable overlay width from **1000–1800 px** and font size from **16–44 pt**.
- Custom active-line color with White, Sakura, Spotify, Cyan, and Gold presets.

### Language and lyrics

- Synchronized `.lrc` lyric parsing for line-level timing.
- Original native script mode for Devanagari, Japanese, Korean, and other scripts.
- English meaning mode for translated lyrics.
- English-letter mode for romanized lyrics, including Hinglish and Romaji-style output.
- Local lyric caching to reduce repeated network requests.
- Graceful fallback behavior when a translation or romanization request is unavailable.

### Motion and gaming

- Smooth Float Up transition for a gentle upward lyric glide.
- Instant Pop transition for a direct, minimal change.
- Game Mode with click-through support so the overlay does not steal mouse input.
- Borderless Windowed / Windowed Fullscreen guidance for the most reliable game overlay behavior.
- System tray controls for visibility, language, position, display mode, transition, preview, settings, and exit.

## Settings, without the clutter

The settings experience is organized into three focused tabs:

| Tab | Controls |
| --- | --- |
| **Appearance** | Position, width, font size, active-line color, and position lock |
| **Language & Script** | Romanized / Hinglish, English meaning, original script, and lyric context |
| **Gaming & Effects** | Click-through Game Mode, Float Up / Instant Pop, and native media status |

The interface uses a dark indigo palette, frosted cards, Sakura pink accents, and a Japanese night background so the controls feel like part of the same listening experience rather than a generic utility dialog.

<div align="center">

<img src="assets/settings-appearance.png" alt="Celestial Whisper Appearance settings with overlay position, width, font size, and color controls" width="88%" />

<sub>The Appearance tab brings the most-used overlay controls into one focused panel.</sub>

</div>

## Installation

### Requirements

- Windows 10 (1809+) or Windows 11
- Python **3.10 or newer**
- Spotify Desktop or Spotify Web Player for playback detection

### 1. Clone the project

```bash
git clone https://github.com/Legend-1s-here/Celestial-Whisper.git
cd Celestial-Whisper
```

### 2. Install dependencies

```bash
py -m pip install -r requirements.txt
```

### 3. Launch

For the regular launcher:

```bash
py main.py
```

For a silent Windows launch without a terminal window, use `Celestial Whisper.vbs` or `run.bat`. You can also create Desktop and Start Menu shortcuts with:

```powershell
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
```

Play a song on Spotify and the overlay will begin listening for the active track. If you want to see the experience before opening Spotify, choose **Preview Sample Lyrics** from the system tray.

## Controls at a glance

| Action | How |
| --- | --- |
| Move the overlay | Click and drag the lyric window |
| Open settings | Double-click the overlay or choose **Settings** from the tray |
| Change position | Overlay context menu or tray → **Position** |
| Change script | Tray → **Lyrics Script** |
| Change context | Tray → **Lyrics Display** |
| Change motion | Tray → **Transition Effect** |
| Enable Game Mode | Tray → **Game Mode (Click-Through Overlay)** |
| Preview the experience | Tray → **Preview Sample Lyrics** |
| Show / hide | Click the ♫ tray icon |
| Exit | Tray or overlay context menu → **Exit** |

## Project anatomy

```text
Celestial-Whisper/
├── main.py                    # Application controller and preview mode
├── overlay.py                 # Transparent, draggable lyrics window
├── settings_ui.py             # Sakura-themed tabbed settings dialog
├── spotify_client.py          # Windows Media Session worker
├── media_monitor.ps1          # Playback metadata stream
├── lyrics_fetcher.py          # LRC parsing, caching, translation, romanization
├── tray.py                    # Windows system tray menu and actions
├── config.py                  # Persistent configuration management
├── config.example.json        # Example configuration
├── create_shortcut.ps1        # Desktop and Start Menu shortcut helper
├── Celestial Whisper.vbs      # Silent Windows launcher
├── run.bat                    # Batch launcher
├── japanese_bg.jpg            # Settings background artwork
├── app.ico                    # Application icon
├── requirements.txt           # Python dependencies
└── assets/
    ├── celestial-whisper-banner.png
    ├── floating-lyrics-example.png
    └── settings-appearance.png
```

## Design language

Celestial Whisper is intentionally soft: midnight indigo, Sakura pink, glass-like panels, luminous text, and just enough motion to make timing feel alive. The visual direction takes cues from Japanese night scenes and music-player minimalism without turning the overlay into another dashboard competing for attention.

## Notes

- This project is designed for **Windows** because playback detection and click-through behavior use Windows media and window APIs.
- For the most reliable game behavior, use **Borderless Windowed** or **Windowed Fullscreen** rather than exclusive fullscreen.
- Lyric availability and synchronization depend on the external lyric sources used by `syncedlyrics`.
- Translation and romanization require network access when a requested variant is not already cached.

## License

Celestial Whisper is released under the [MIT License](./LICENSE).

<div align="center">

**Made for the moments when the song is part of the scene.**

</div>
