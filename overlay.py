import sys
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QMenu, QApplication
)
from PyQt6.QtGui import QFont, QColor, QCursor

class LyricsFrame(QWidget):
    """Container holding previous, current, and upcoming lyric lines."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.op_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.op_effect)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 10, 30, 10)
        self.layout.setSpacing(6)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
            sh.setBlurRadius(16)
            sh.setColor(QColor(0, 0, 0, 255))
            sh.setOffset(1, 2)
            lbl.setGraphicsEffect(sh)
            self.layout.addWidget(lbl)

    def apply_style(self, font_size: int, text_color: str, context_mode: str):
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
        self.anim_group = None

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

        self.frame_a = LyricsFrame(self)
        self.frame_b = LyricsFrame(self)
        self.frame_b.hide()

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
        self.frame_a.setGeometry(0, 0, width, height)
        self.frame_b.setGeometry(0, 0, width, height)

        self.frame_a.apply_style(font_size, text_color, context_mode)
        self.frame_b.apply_style(font_size, text_color, context_mode)

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

    def force_topmost(self):
        try:
            import ctypes
            hwnd = int(self.winId())
            HWND_TOPMOST = ctypes.c_void_p(-1)
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            SWP_SHOWWINDOW = 0x0040
            ctypes.windll.user32.SetWindowPos(ctypes.c_void_p(hwnd), HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW)
        except Exception:
            pass

    def showEvent(self, event):
        super().showEvent(event)
        self.force_topmost()

    def setLyrics(self, prev_line: str, curr_line: str, next_line: str, animate: bool = True):
        # Ignore redundant calls when lyric has not advanced
        if curr_line == self._current_text:
            return

        old_curr = self._current_text
        self._current_text = curr_line
        trans_mode = self.config.get("transition_mode", "float")

        # Instant mode, cold start, or non-animated update
        if not animate or trans_mode == "instant" or not old_curr:
            self._apply_instant(prev_line, curr_line, next_line)
            return

        # Stop any active animation immediately and finalize
        if self.anim_group and self.anim_group.state() == QParallelAnimationGroup.State.Running:
            self.anim_group.stop()
            self._finalize_transition(self._pending_prev, self._pending_curr, self._pending_next)

        self._pending_prev = prev_line
        self._pending_curr = curr_line
        self._pending_next = next_line

        context_mode = self.config.get("context_mode", "next_only")
        font_size = self.config.get("font_size", 24)

        if context_mode == "next_only":
            delta = self.frame_a.lbl_next.y() - self.frame_a.lbl_curr.y()
            if delta <= 10:
                delta = max(35, int(font_size * 1.5))

            # Frame A keeps old current line floating up; clear next to prevent double vision
            self.frame_a.lbl_next.setText("")

            # Frame B has the incoming state
            self.frame_b.lbl_prev.setText("")
            self.frame_b.lbl_curr.setText(curr_line)
            self.frame_b.lbl_next.setText(next_line)

        elif context_mode == "both":
            delta = self.frame_a.lbl_curr.y() - self.frame_a.lbl_prev.y()
            if delta <= 10:
                delta = max(35, int(font_size * 1.5))

            self.frame_a.lbl_next.setText("")

            self.frame_b.lbl_prev.setText(old_curr)
            self.frame_b.lbl_curr.setText(curr_line)
            self.frame_b.lbl_next.setText(next_line)

        else:  # "none" (1 line)
            delta = max(35, int(font_size * 1.4))
            self.frame_b.lbl_curr.setText(curr_line)

        self.frame_b.move(0, delta)
        self.frame_b.op_effect.setOpacity(0.3)
        self.frame_b.show()

        self.anim_group = QParallelAnimationGroup(self)

        a1 = QPropertyAnimation(self.frame_a, b"pos")
        a1.setDuration(360)
        a1.setStartValue(QPoint(0, 0))
        a1.setEndValue(QPoint(0, -delta))
        a1.setEasingCurve(QEasingCurve.Type.OutCubic)

        o1 = QPropertyAnimation(self.frame_a.op_effect, b"opacity")
        o1.setDuration(360)
        o1.setStartValue(1.0)
        o1.setEndValue(0.0)

        a2 = QPropertyAnimation(self.frame_b, b"pos")
        a2.setDuration(360)
        a2.setStartValue(QPoint(0, delta))
        a2.setEndValue(QPoint(0, 0))
        a2.setEasingCurve(QEasingCurve.Type.OutCubic)

        o2 = QPropertyAnimation(self.frame_b.op_effect, b"opacity")
        o2.setDuration(360)
        o2.setStartValue(0.3)
        o2.setEndValue(1.0)

        self.anim_group.addAnimation(a1)
        self.anim_group.addAnimation(o1)
        self.anim_group.addAnimation(a2)
        self.anim_group.addAnimation(o2)

        self.anim_group.finished.connect(lambda: self._finalize_transition(prev_line, curr_line, next_line))
        self.anim_group.start()

    def _finalize_transition(self, prev_line: str, curr_line: str, next_line: str):
        self.frame_a.lbl_prev.setText(prev_line)
        self.frame_a.lbl_curr.setText(curr_line)
        self.frame_a.lbl_next.setText(next_line)
        self.frame_a.move(0, 0)
        self.frame_a.op_effect.setOpacity(1.0)
        self.frame_b.hide()
        self.frame_b.move(0, 0)

    def _apply_instant(self, prev_line: str, curr_line: str, next_line: str):
        if self.anim_group and self.anim_group.state() == QParallelAnimationGroup.State.Running:
            self.anim_group.stop()
        self.frame_a.lbl_prev.setText(prev_line)
        self.frame_a.lbl_curr.setText(curr_line)
        self.frame_a.lbl_next.setText(next_line)
        self.frame_a.move(0, 0)
        self.frame_a.op_effect.setOpacity(1.0)
        self.frame_b.hide()
        self.frame_b.move(0, 0)

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
