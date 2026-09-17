<div align="center">

# 🌸 Celestial Whisper
### 浮動歌詞オーバーレイ • Floating Spotify Lyrics Overlay for Windows

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![Platform](https://img.shields.io/badge/Platform-Windows_10_|_11-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Spotify](https://img.shields.io/badge/Spotify-Free_&_Premium-1ED760?style=for-the-badge&logo=spotify&logoColor=white)](https://spotify.com)
[![License](https://img.shields.io/badge/License-MIT-F38BA8?style=for-the-badge)](LICENSE)

<p align="center">
  <b>A lightweight, beautiful desktop overlay that displays real-time time-synchronized floating lyrics on top of all windows, games, and videos while listening to Spotify.</b>
</p>

</div>

---

## ✨ Features

- 🌟 **100% Free — No Spotify Premium or Developer API Keys Needed**
  - Uses Windows Native Media Transport to track Spotify playback directly from Windows.
  - Works out of the box with **Spotify Free**, **Spotify Premium**, **Spotify Desktop App**, and **Spotify Web Player**.
  - No `403 Forbidden` API limitations or complicated developer portal setup required!

- 🌸 **Japanese Sakura Night Theme**
  - Atmospheric dark-mode Settings UI featuring **Mount Fuji**, a traditional **Torii gate**, a **5-story Pagoda**, a glowing **crescent moon**, and blossoming **Sakura cherry branches**.
  - Frosted glass translucent cards with Sakura pink accents.

- 🪟 **Floating Translucent Text (No Box)**
  - Frameless and completely transparent — floats seamlessly above full-screen games, coding IDEs, browsers, or movies without an annoying opaque box.
  - High-contrast glowing drop shadows ensure lyrics are crisp and readable over both dark and bright backgrounds.

- 📍 **Dual Positioning & Free Drag-and-Drop**
  - **Top of the Screen**: Positioned at the top edge (ideal for staying clear of game HUDs and bottom taskbars).
  - **Bottom Center**: Classic cinema subtitle style.
  - **Free Dragging**: Click and drag the floating text anywhere on your screen with your mouse!

- 📜 **Flexible Lyrics Display Modes**
  - **Next Lyric Only (2 lines)**: Displays the bold active line and the upcoming line (no past lyrics).
  - **Both Previous & Next (3 lines)**: Full 3-line cinema view.
  - **Current Lyric Only (1 line)**: Ultra-minimalist single line.

- 📏 **Customizable Width & Font Size**
  - Adjustable overlay width slider from **`1000 px` to `1800 px`** to eliminate any line wrapping or edge clipping.
  - Font size slider from **`16 pt` to `44 pt`**.
  - Color presets including **Sakura Pink (`#FFB7C5`)**, **Crisp White**, **Spotify Green**, **Neon Cyan**, and **Sunset Gold**.

- ⚡ **Worldwide Language Support & Auto Caching**
  - Fetches synced `.lrc` lyrics automatically via LRCLIB for English, Japanese, Korean, Spanish, Hindi, and tracks worldwide.
  - Automatically caches lyrics locally for instantaneous loading on repeat listens.

- 🚀 **Native App Launcher (No Terminal Window!)**
  - Desktop shortcut and Start Menu shortcut included.
  - Runs silently via `pythonw.exe` without opening a command prompt console.

---

## 📥 Installation

### Prerequisites
- **Windows 10 (1809+) or Windows 11**
- **Python 3.10 or higher** (Ensure *"Add Python to PATH"* is checked during installation)

### 1. Clone the Repository
```bash
git clone https://github.com/Legend-1s-here/Celestial-Whisper.git
cd Celestial-Whisper
```

### 2. Install Dependencies
```bash
py -m pip install -r requirements.txt
```
*(Or `pip install -r requirements.txt`)*

### 3. Create Desktop & Start Menu Shortcut (Recommended)
Run the included PowerShell script to place a **Celestial Whisper** shortcut directly on your Desktop and Start Menu:
```powershell
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
```

---

## 🎮 How to Run

You have several ways to launch the app:

1. **Desktop Shortcut**: Double-click the **Celestial Whisper** icon on your Desktop (no terminal window will open).
2. **Start Menu**: Press the **Windows Key**, type `Celestial Whisper`, and press `Enter`.
3. **Folder Launcher**: Double-click `Celestial Whisper.vbs` or `run.bat`.
4. **Terminal**: Run `py main.py` or `pythonw main.py`.

Once running, play any song on Spotify and watch the lyrics float on your screen in real time!

---

## ⌨️ Controls & Shortcuts

| Action | Control |
|---|---|
| **Move Overlay** | Click and drag the floating lyrics with your mouse |
| **Open Settings** | Double-click the lyrics (or right-click $\rightarrow$ *Settings*) |
| **Quick Position Switch** | Right-click the lyrics $\rightarrow$ *Position* (*Top* or *Bottom Center*) |
| **Toggle Show / Hide** | Left-click the **♫** tray icon in your Windows Taskbar |
| **Change Lyrics Mode** | Right-click the **♫** tray icon $\rightarrow$ *Lyrics Display* (*Next Lyric Only*, *Both*, *Current Only*) |
| **Exit** | Right-click the tray icon or overlay $\rightarrow$ *Exit* |

---

## 📁 Project Structure

```
Celestial-Whisper/
├── main.py                 # Application entry point & controller
├── overlay.py              # Frameless, transparent floating lyrics window
├── settings_ui.py          # Japanese Sakura themed Settings UI
├── spotify_client.py       # Dual-engine Spotify & Windows Media worker
├── media_monitor.ps1       # Real-time Windows Media Session stream
├── lyrics_fetcher.py       # Synced .lrc lyrics parser with local caching
├── tray.py                 # Windows Taskbar system tray menu
├── config.py               # Settings manager (loads/saves config.json)
├── config.example.json     # Configuration template
├── create_shortcut.ps1     # 1-click Desktop & Start Menu shortcut creator
├── Celestial Whisper.vbs   # Silent native app launcher
├── run.bat                 # Standard batch launcher
├── app.ico                 # Custom Sakura ♫ application icon
├── japanese_bg.jpg         # Japanese theme background art
├── requirements.txt        # Python package dependencies
└── README.md               # Documentation
```

---

## 🛠️ Built With

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — High-performance cross-platform GUI toolkit
- [syncedlyrics](https://github.com/rtkay123/syncedlyrics) — Time-synced `.lrc` lyrics fetching from LRCLIB
- [spotipy](https://spotipy.readthedocs.io/) — Python client for the Spotify Web API
- Windows Runtime (`Windows.Media.Control`) — Zero-API-key native Windows playback tracking

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

<div align="center">
  <sub>Made with 🌸 for music lovers everywhere.</sub>
</div>
