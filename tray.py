from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import pyqtSignal, Qt

def create_music_tray_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QColor("#FF8DA1"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 28, 28)

    painter.setPen(QColor("#121218"))
    font = QFont("Segoe UI Symbol", 16, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "♫")
    painter.end()

    return QIcon(pixmap)

class SystemTray(QSystemTrayIcon):
    toggle_overlay = pyqtSignal()
    open_settings = pyqtSignal()
    position_changed = pyqtSignal(str)
    context_mode_changed = pyqtSignal(str)
    language_mode_changed = pyqtSignal(str)
    test_lyrics = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(create_music_tray_icon())
        self.setToolTip("Celestial Whisper — Spotify Floating Lyrics")
        self._build_menu()
        self.activated.connect(self._on_activated)

    def _build_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #161722;
                color: #FFFFFF;
                border: 1px solid #3d3e52;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #FF8DA1;
                color: #121218;
                font-weight: bold;
            }
            QMenu::separator {
                height: 1px;
                background-color: #323348;
                margin: 4px 0px;
            }
        """)

        self.action_toggle = menu.addAction("👁️ Toggle Lyrics Overlay")
        self.action_toggle.triggered.connect(self.toggle_overlay.emit)

        # Position submenu
        pos_menu = menu.addMenu("📍 Position")
        self.action_top = pos_menu.addAction("Top of Screen")
        self.action_bottom = pos_menu.addAction("Bottom Center")
        self.action_top.triggered.connect(lambda: self.position_changed.emit("top"))
        self.action_bottom.triggered.connect(lambda: self.position_changed.emit("bottom"))

        # Language submenu
        lang_menu = menu.addMenu("🌐 Language")
        self.action_lang_en = lang_menu.addAction("English Translation")
        self.action_lang_rom = lang_menu.addAction("English Romanized (Hinglish)")
        self.action_lang_orig = lang_menu.addAction("Original Language")
        self.action_lang_en.triggered.connect(lambda: self.language_mode_changed.emit("english"))
        self.action_lang_rom.triggered.connect(lambda: self.language_mode_changed.emit("romanized"))
        self.action_lang_orig.triggered.connect(lambda: self.language_mode_changed.emit("original"))

        # Lyrics Display mode submenu
        ctx_menu = menu.addMenu("📜 Lyrics Display")
        self.action_next_only = ctx_menu.addAction("Next Lyric Only (2 lines)")
        self.action_both = ctx_menu.addAction("Both Prev & Next (3 lines)")
        self.action_none = ctx_menu.addAction("Current Lyric Only (1 line)")
        self.action_next_only.triggered.connect(lambda: self.context_mode_changed.emit("next_only"))
        self.action_both.triggered.connect(lambda: self.context_mode_changed.emit("both"))
        self.action_none.triggered.connect(lambda: self.context_mode_changed.emit("none"))

        menu.addSeparator()

        self.action_test = menu.addAction("▶ Preview Sample Lyrics")
        self.action_test.triggered.connect(self.test_lyrics.emit)

        self.action_settings = menu.addAction("🌸 Settings...")
        self.action_settings.triggered.connect(self.open_settings.emit)

        menu.addSeparator()
        self.action_exit = menu.addAction("❌ Exit")

        self.setContextMenu(menu)

    def _on_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.toggle_overlay.emit()
