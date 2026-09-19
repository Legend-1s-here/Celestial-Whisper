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
  - No `403 Forbidden` API limitations or login setup required!

- 🌐 **English Lyrics Options (Translation & Transliteration)**
  - **English Translation**: Translates Hindi, Japanese, Korean, Spanish, and foreign songs line-by-line into English meaning while preserving exact millisecond playback sync!
  - **English Romanized (Hinglish / Latin Alphabet)**: Converts Devanagari Hindi into clean, readable English alphabet lyrics (e.g., *"Kesariya tera ishq hai piya"*).
  - **Original Language**: Keep native scripts whenever preferred.
  - Switch on the fly via Settings or System Tray!

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

- 🌊 **Smooth Floating Upward Motion (Float vs Pop)**
  - Upcoming lines smoothly float and glide upwards into place as the song progresses with fluid cubic easing, making lyrics effortless to read without jarring jumps.
  - Option to toggle between **Smooth Float Up** (gliding animation) and **Instant Pop** (direct switch) in Settings and System Tray!

- 🎮 **Gaming Mode & Fullscreen Game Support**
  - **Always on Top of Games**: High-frequency Win32 topmost keep-alive maintains the overlay in the foreground, even when games take focus or resolution changes.
  - **Click-Through (Mouse Passthrough)**: Toggle Game Mode on to let 100% of mouse clicks pass straight through into your game without interruption! You can play, aim, and shoot while reading lyrics.
  - Easily toggle Game Mode on/off anytime from the **♫ System Tray** icon or Settings.
  - *(Note: Ensure your game's display setting is set to **Borderless Windowed** / **Windowed Fullscreen** so Windows Desktop Window Manager can render overlays).*

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

### 3. Create Desktop & Start Menu Shortcut (Recommended)
Run the included PowerShell script to place a **Celestial Whisper** shortcut directly on your Desktop and Start Menu:
```powershell
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
```

---

## 🎮 How to Run

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
| **Switch Language Mode** | Right-click the **♫** tray icon $\rightarrow$ *Language* (*English Translation*, *Hinglish*, *Original*) |
| **Switch Transition Style** | Right-click overlay or tray $\rightarrow$ *Transition Effect* (*Float Up* or *Instant Pop*) |
| **Change Lyrics Mode** | Right-click the **♫** tray icon $\rightarrow$ *Lyrics Display* (*Next Lyric Only*, *Both*, *Current Only*) |
| **Toggle Game Mode** | Right-click the **♫** tray icon $\rightarrow$ *🎮 Game Mode (Click-Through Overlay)* |
| **Toggle Show / Hide** | Left-click the **♫** tray icon in your Windows Taskbar |
| **Exit** | Right-click the tray icon or overlay $\rightarrow$ *Exit* |

---

## 📁 Project Structure

```
Celestial-Whisper/
├── main.py                 # Application entry point & controller
├── overlay.py              # Frameless, transparent floating lyrics window
├── settings_ui.py          # Japanese Sakura themed Settings UI with English options
├── spotify_client.py       # Windows Media worker (Spotify Free & Premium)
├── media_monitor.ps1       # Real-time Windows Media Session stream
├── lyrics_fetcher.py       # Synced .lrc lyrics parser with translation & caching
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

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

<div align="center">
  <sub>Made with 🌸 for music lovers everywhere.</sub>
</div>
