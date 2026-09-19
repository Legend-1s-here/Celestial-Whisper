import sys
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect,
    QMenu, QApplication
)
from PyQt6.QtGui import QFont, QColor


class FloatingLyricsOverlay(QWidget):
    open_settings_requested = pyqtSignal()
    position_mode_changed = pyqtSignal(str)
    transition_mode_changed = pyqtSignal(str)   # kept for compatibility

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.drag_position = QPoint()
        self.is_dragging = False
        self._current_text = ""

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

        self.lbl_prev = QLabel(self)
        self.lbl_prev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_prev.setWordWrap(True)

        self.lbl_curr = QLabel(self)
        self.lbl_curr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_curr.setWordWrap(True)

        self.lbl_next = QLabel(self)
        self.lbl_next.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_next.setWordWrap(True)

        for lbl in (self.lbl_prev, self.lbl_curr, self.lbl_next):
            sh = QGraphicsDropShadowEffect(lbl)
            sh.setBlurRadius(18)
            sh.setColor(QColor(0, 0, 0, 255))
            sh.setOffset(1, 2)
            lbl.setGraphicsEffect(sh)
            layout.addWidget(lbl)

        self.setLyrics(
            prev_line="",
            curr_line="🎶 Floating Lyrics Ready",
            next_line="Play any song on Spotify • Double-click for settings",
        )

    def force_topmost(self):
        try:
            import ctypes
            hwnd = int(self.winId())
            HWND_TOPMOST = ctypes.c_void_p(-1)
            SWP_NOMOVE    = 0x0002
            SWP_NOSIZE    = 0x0001
            SWP_NOACTIVATE = 0x0010
            SWP_SHOWWINDOW = 0x0040
            ctypes.windll.user32.SetWindowPos(
                ctypes.c_void_p(hwnd), HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
            )
        except Exception:
            pass
        self.show()
        self.raise_()

    def showEvent(self, event):
        super().showEvent(event)
        self.force_topmost()

    def apply_config(self, config: dict = None):
        if config:
            self.config = config

        font_size    = self.config.get("font_size", 24)
        text_color   = self.config.get("text_color", "#FFB7C5")
        context_mode = self.config.get("context_mode", "next_only")
        width  = max(1200, self.config.get("window_width", 1400))
        height = max(220,  self.config.get("window_height", 240))

        self.setFixedSize(width, height)

        font_family = "Segoe UI, Meiryo, 'Hiragino Sans', Montserrat, Helvetica, Arial, sans-serif"
        sub_pt = max(12, int(font_size * 0.68))

        sub_style = f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.60);
                font-family: {font_family};
                font-size: {sub_pt}pt;
                font-weight: 500;
                background: transparent;
                padding: 2px 0px;
            }}
        """
        curr_style = f"""
            QLabel {{
                color: {text_color};
                font-family: {font_family};
                font-size: {font_size}pt;
                font-weight: 700;
                background: transparent;
                padding: 4px 0px;
                letter-spacing: 0.5px;
            }}
        """

        self.lbl_prev.setStyleSheet(sub_style)
        self.lbl_curr.setStyleSheet(curr_style)
        self.lbl_next.setStyleSheet(sub_style)

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
        self.force_topmost()

    def setLyrics(self, prev_line: str, curr_line: str, next_line: str, **kwargs):
        if curr_line == self._current_text:
            return
        self._current_text = curr_line
        self.lbl_prev.setText(prev_line)
        self.lbl_curr.setText(curr_line)
        self.lbl_next.setText(next_line)

    def showStatus(self, message: str, subtitle: str = ""):
        self.setLyrics("", message, subtitle)

    # ── Mouse handling ────────────────────────────────────────────────────────

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
        act_top    = pos_menu.addAction("Top of Screen")
        act_bottom = pos_menu.addAction("Bottom Center")
        act_top.triggered.connect(   lambda: self._change_position("top"))
        act_bottom.triggered.connect(lambda: self._change_position("bottom"))

        menu.addSeparator()
        act_settings = menu.addAction("🌸 Settings...")
        act_settings.triggered.connect(self.open_settings_requested.emit)

        menu.addSeparator()
        act_exit = menu.addAction("❌ Exit")
        act_exit.triggered.connect(QApplication.quit)

        menu.exec(event.globalPos())

    def _change_position(self, mode: str):
        self.set_position_mode(mode)
        self.position_mode_changed.emit(mode)
