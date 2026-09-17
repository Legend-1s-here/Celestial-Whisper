import sys
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect,
    QMenu, QApplication
)
from PyQt6.QtGui import QFont, QColor, QCursor

class FloatingLyricsOverlay(QWidget):
    open_settings_requested = pyqtSignal()
    position_mode_changed = pyqtSignal(str)  # "top" or "bottom"

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.drag_position = QPoint()
        self.is_dragging = False

        self._init_ui()
        self.apply_config()

    def _init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 10, 30, 10)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Previous line
        self.lbl_prev = QLabel(self)
        self.lbl_prev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_prev.setWordWrap(True)

        # Current line (active)
        self.lbl_curr = QLabel(self)
        self.lbl_curr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_curr.setWordWrap(True)

        # Next line
        self.lbl_next = QLabel(self)
        self.lbl_next.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_next.setWordWrap(True)

        # Drop shadows for 100% legibility on any background
        self.shadow_prev = QGraphicsDropShadowEffect(self)
        self.shadow_prev.setBlurRadius(12)
        self.shadow_prev.setColor(QColor(0, 0, 0, 230))
        self.shadow_prev.setOffset(1, 2)
        self.lbl_prev.setGraphicsEffect(self.shadow_prev)

        self.shadow_curr = QGraphicsDropShadowEffect(self)
        self.shadow_curr.setBlurRadius(16)
        self.shadow_curr.setColor(QColor(0, 0, 0, 255))
        self.shadow_curr.setOffset(1, 2)
        self.lbl_curr.setGraphicsEffect(self.shadow_curr)

        self.shadow_next = QGraphicsDropShadowEffect(self)
        self.shadow_next.setBlurRadius(12)
        self.shadow_next.setColor(QColor(0, 0, 0, 230))
        self.shadow_next.setOffset(1, 2)
        self.lbl_next.setGraphicsEffect(self.shadow_next)

        layout.addWidget(self.lbl_prev)
        layout.addWidget(self.lbl_curr)
        layout.addWidget(self.lbl_next)

        self.setLyrics(
            prev_line="",
            curr_line="🎶 Floating Lyrics Ready",
            next_line="Play any song on Spotify • Double-click for settings"
        )

    def apply_config(self, config: dict = None):
        if config:
            self.config = config

        font_size = self.config.get("font_size", 26)
        text_color = self.config.get("text_color", "#FFFFFF")
        context_mode = self.config.get("context_mode", "next_only")
        width = max(1200, self.config.get("window_width", 1400))
        height = max(220, self.config.get("window_height", 240))

        self.setFixedSize(width, height)

        font_family = "Segoe UI, Meiryo, 'Hiragino Sans', Montserrat, Helvetica, Arial, sans-serif"

        # Previous Line Style
        self.lbl_prev.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.48);
                font-family: {font_family};
                font-size: {max(12, int(font_size * 0.65))}pt;
                font-weight: 500;
                background: transparent;
                padding: 2px 0px;
            }}
        """)

        # Current Line Style
        self.lbl_curr.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-family: {font_family};
                font-size: {font_size}pt;
                font-weight: 700;
                background: transparent;
                padding: 4px 0px;
                letter-spacing: 0.5px;
            }}
        """)

        # Next Line Style
        self.lbl_next.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.48);
                font-family: {font_family};
                font-size: {max(12, int(font_size * 0.65))}pt;
                font-weight: 500;
                background: transparent;
                padding: 2px 0px;
            }}
        """)

        # Context Mode:
        # "both": show previous + next
        # "next_only": show ONLY next, no previous
        # "none": only show current line
        if context_mode == "next_only":
            self.lbl_prev.setVisible(False)
            self.lbl_next.setVisible(True)
        elif context_mode == "none":
            self.lbl_prev.setVisible(False)
            self.lbl_next.setVisible(False)
        else:  # "both"
            self.lbl_prev.setVisible(True)
            self.lbl_next.setVisible(True)

        pos_mode = self.config.get("position", "bottom")
        self.set_position_mode(pos_mode)

    def set_position_mode(self, mode: str):
        screen = QApplication.primaryScreen()
        if not screen:
            return

        geo = screen.availableGeometry()
        w = self.width()
        h = self.height()
        x = geo.x() + (geo.width() - w) // 2

        if mode == "top":
            y = geo.y() + 35
        else:  # bottom
            y = geo.y() + geo.height() - h - 45

        self.move(x, y)
        self.config["position"] = mode

    def setLyrics(self, prev_line: str, curr_line: str, next_line: str):
        self.lbl_prev.setText(prev_line)
        self.lbl_curr.setText(curr_line)
        self.lbl_next.setText(next_line)

    def showStatus(self, message: str, subtitle: str = ""):
        self.setLyrics("", message, subtitle)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.config.get("lock_position", False):
                self.is_dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and (event.buttons() & Qt.MouseButton.LeftButton):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_settings_requested.emit()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
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
                padding: 6px 22px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #FF8DA1;
                color: #121216;
                font-weight: bold;
            }
            QMenu::separator {
                height: 1px;
                background-color: #323348;
                margin: 4px 0px;
            }
        """)

        pos_menu = menu.addMenu("📍 Position")
        top_action = pos_menu.addAction("Top of Screen")
        bottom_action = pos_menu.addAction("Bottom Center (Subtitles)")

        if self.config.get("position") == "top":
            top_action.setText("✓ Top of Screen")
        else:
            bottom_action.setText("✓ Bottom Center (Subtitles)")

        menu.addSeparator()

        settings_action = menu.addAction("🌸 Settings...")
        hide_action = menu.addAction("👁️ Hide Overlay")
        menu.addSeparator()
        exit_action = menu.addAction("❌ Exit")

        action = menu.exec(QCursor.pos())
        if action == top_action:
            self.set_position_mode("top")
            self.position_mode_changed.emit("top")
        elif action == bottom_action:
            self.set_position_mode("bottom")
            self.position_mode_changed.emit("bottom")
        elif action == settings_action:
            self.open_settings_requested.emit()
        elif action == hide_action:
            self.hide()
        elif action == exit_action:
            QApplication.quit()
