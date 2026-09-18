import sys
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import (
    QWidget, QLabel, QGraphicsDropShadowEffect, QMenu, QApplication
)
from PyQt6.QtGui import QFont, QColor, QCursor

class FloatingLyricsOverlay(QWidget):
    open_settings_requested = pyqtSignal()
    position_mode_changed = pyqtSignal(str)     # "top" or "bottom"
    transition_mode_changed = pyqtSignal(str)   # "float" or "instant"

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.drag_position = QPoint()
        self.is_dragging = False

        self._current_text = ""
        self._pending_prev = ""
        self._pending_curr = ""
        self._pending_next = ""
        self.anim = None

        self.slot_h = 75
        self.y_curr = 45
        self.y_next = 120
        self.y_out = -30
        self.y_in = 195
        self.y_prev = 15

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

        # Continuous canvas that smoothly glides without disappearing
        self.canvas = QWidget(self)

        self.lbl_out = QLabel(self.canvas)
        self.lbl_prev = QLabel(self.canvas)
        self.lbl_curr = QLabel(self.canvas)
        self.lbl_next = QLabel(self.canvas)
        self.lbl_in = QLabel(self.canvas)

        for lbl in (self.lbl_out, self.lbl_prev, self.lbl_curr, self.lbl_next, self.lbl_in):
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setWordWrap(True)
            sh = QGraphicsDropShadowEffect(lbl)
            sh.setBlurRadius(16)
            sh.setColor(QColor(0, 0, 0, 255))
            sh.setOffset(1, 2)
            lbl.setGraphicsEffect(sh)

        self.setLyrics(
            prev_line="",
            curr_line="🎶 Floating Lyrics Ready",
            next_line="Play any song on Spotify • Double-click for settings",
            animate=False
        )

    def apply_config(self, config: dict = None):
        if config:
            self.config = config

        font_size = self.config.get("font_size", 24)
        text_color = self.config.get("text_color", "#FFB7C5")
        context_mode = self.config.get("context_mode", "next_only")
        width = max(1200, self.config.get("window_width", 1400))
        height = max(220, self.config.get("window_height", 240))

        self.setFixedSize(width, height)
        self.canvas.setGeometry(0, 0, width, height + 300)

        font_family = "Segoe UI, Meiryo, 'Hiragino Sans', Montserrat, Helvetica, Arial, sans-serif"
        sub_pt = max(12, int(font_size * 0.68))

        sub_style = f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.62);
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
                padding: 2px 0px;
                letter-spacing: 0.5px;
            }}
        """

        self.lbl_out.setStyleSheet(sub_style)
        self.lbl_prev.setStyleSheet(sub_style)
        self.lbl_curr.setStyleSheet(curr_style)
        self.lbl_next.setStyleSheet(sub_style)
        self.lbl_in.setStyleSheet(sub_style)

        pad_x = 40
        label_w = width - (pad_x * 2)

        if context_mode == "next_only":
            self.slot_h = 74
            self.y_curr = (height - (self.slot_h * 2)) // 2
            self.y_next = self.y_curr + self.slot_h
            self.y_out = self.y_curr - self.slot_h
            self.y_in = self.y_next + self.slot_h

            self.lbl_prev.setVisible(False)
            self.lbl_next.setVisible(True)

            self.lbl_out.setGeometry(pad_x, self.y_out, label_w, self.slot_h)
            self.lbl_curr.setGeometry(pad_x, self.y_curr, label_w, self.slot_h)
            self.lbl_next.setGeometry(pad_x, self.y_next, label_w, self.slot_h)
            self.lbl_in.setGeometry(pad_x, self.y_in, label_w, self.slot_h)

        elif context_mode == "both":
            self.slot_h = 58
            self.y_prev = (height - (self.slot_h * 3)) // 2
            self.y_curr = self.y_prev + self.slot_h
            self.y_next = self.y_curr + self.slot_h
            self.y_out = self.y_prev - self.slot_h
            self.y_in = self.y_next + self.slot_h

            self.lbl_prev.setVisible(True)
            self.lbl_next.setVisible(True)

            self.lbl_out.setGeometry(pad_x, self.y_out, label_w, self.slot_h)
            self.lbl_prev.setGeometry(pad_x, self.y_prev, label_w, self.slot_h)
            self.lbl_curr.setGeometry(pad_x, self.y_curr, label_w, self.slot_h)
            self.lbl_next.setGeometry(pad_x, self.y_next, label_w, self.slot_h)
            self.lbl_in.setGeometry(pad_x, self.y_in, label_w, self.slot_h)

        else:  # "none" (1 line)
            self.slot_h = 75
            self.y_curr = (height - self.slot_h) // 2
            self.y_out = self.y_curr - self.slot_h
            self.y_in = self.y_curr + self.slot_h

            self.lbl_prev.setVisible(False)
            self.lbl_next.setVisible(False)

            self.lbl_out.setGeometry(pad_x, self.y_out, label_w, self.slot_h)
            self.lbl_curr.setGeometry(pad_x, self.y_curr, label_w, self.slot_h)
            self.lbl_in.setGeometry(pad_x, self.y_in, label_w, self.slot_h)

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

    def setLyrics(self, prev_line: str, curr_line: str, next_line: str, incoming_line: str = "", animate: bool = True):
        # Ignore redundant tick calls when lyric hasn't changed
        if curr_line == self._current_text:
            return

        old_curr = self._current_text
        self._current_text = curr_line
        trans_mode = self.config.get("transition_mode", "float")

        # Instant mode, cold start, or non-animated update
        if not animate or trans_mode == "instant" or not old_curr:
            self._apply_instant(prev_line, curr_line, next_line)
            return

        # Stop any active animation immediately
        if self.anim and self.anim.state() == QPropertyAnimation.State.Running:
            self.anim.stop()
            self._on_finished(self._pending_prev, self._pending_curr, self._pending_next)

        self._pending_prev = prev_line
        self._pending_curr = curr_line
        self._pending_next = next_line

        context_mode = self.config.get("context_mode", "next_only")

        if context_mode == "next_only":
            self.lbl_out.setText(self.lbl_curr.text())
            self.lbl_in.setText(incoming_line)
        elif context_mode == "both":
            self.lbl_out.setText(self.lbl_prev.text())
            self.lbl_in.setText(incoming_line)
        else:  # "none"
            self.lbl_out.setText(self.lbl_curr.text())
            self.lbl_in.setText(curr_line)

        self.canvas.move(0, 0)
        self.anim = QPropertyAnimation(self.canvas, b"pos")
        self.anim.setDuration(340)
        self.anim.setStartValue(QPoint(0, 0))
        self.anim.setEndValue(QPoint(0, -self.slot_h))
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.finished.connect(lambda: self._on_finished(prev_line, curr_line, next_line))
        self.anim.start()

    def _on_finished(self, prev_line: str, curr_line: str, next_line: str):
        self.lbl_prev.setText(prev_line)
        self.lbl_curr.setText(curr_line)
        self.lbl_next.setText(next_line)
        self.lbl_out.setText("")
        self.lbl_in.setText("")
        self.canvas.move(0, 0)

    def _apply_instant(self, prev_line: str, curr_line: str, next_line: str):
        if self.anim and self.anim.state() == QPropertyAnimation.State.Running:
            self.anim.stop()
        self.lbl_prev.setText(prev_line)
        self.lbl_curr.setText(curr_line)
        self.lbl_next.setText(next_line)
        self.lbl_out.setText("")
        self.lbl_in.setText("")
        self.canvas.move(0, 0)

    def showStatus(self, message: str, subtitle: str = ""):
        self.setLyrics("", message, subtitle, animate=False)

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

        # Position submenu
        pos_menu = menu.addMenu("📍 Position")
        top_action = pos_menu.addAction("Top of Screen")
        bottom_action = pos_menu.addAction("Bottom Center (Subtitles)")

        if self.config.get("position") == "top":
            top_action.setText("✓ Top of Screen")
        else:
            bottom_action.setText("✓ Bottom Center (Subtitles)")

        # Transition effect submenu
        trans_menu = menu.addMenu("✨ Transition Effect")
        float_action = trans_menu.addAction("🌸 Smooth Float Up")
        pop_action = trans_menu.addAction("⚡ Instant Pop")

        if self.config.get("transition_mode", "float") == "float":
            float_action.setText("✓ 🌸 Smooth Float Up")
        else:
            pop_action.setText("✓ ⚡ Instant Pop")

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
        elif action == float_action:
            self.config["transition_mode"] = "float"
            self.transition_mode_changed.emit("float")
        elif action == pop_action:
            self.config["transition_mode"] = "instant"
            self.transition_mode_changed.emit("instant")
        elif action == settings_action:
            self.open_settings_requested.emit()
        elif action == hide_action:
            self.hide()
        elif action == exit_action:
            QApplication.quit()
