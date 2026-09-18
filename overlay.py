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

        # High-contrast drop shadows for 100% legibility on any background
        self.shadow_prev = QGraphicsDropShadowEffect(self.lbl_prev)
        self.shadow_prev.setBlurRadius(12)
        self.shadow_prev.setColor(QColor(0, 0, 0, 230))
        self.shadow_prev.setOffset(1, 2)
        self.lbl_prev.setGraphicsEffect(self.shadow_prev)

        self.shadow_curr = QGraphicsDropShadowEffect(self.lbl_curr)
        self.shadow_curr.setBlurRadius(16)
        self.shadow_curr.setColor(QColor(0, 0, 0, 255))
        self.shadow_curr.setOffset(1, 2)
        self.lbl_curr.setGraphicsEffect(self.shadow_curr)

        self.shadow_next = QGraphicsDropShadowEffect(self.lbl_next)
        self.shadow_next.setBlurRadius(12)
        self.shadow_next.setColor(QColor(0, 0, 0, 230))
        self.shadow_next.setOffset(1, 2)
        self.lbl_next.setGraphicsEffect(self.shadow_next)

        self.layout.addWidget(self.lbl_prev)
        self.layout.addWidget(self.lbl_curr)
        self.layout.addWidget(self.lbl_next)

    def apply_style(self, font_size: int, text_color: str, context_mode: str):
        font_family = "Segoe UI, Meiryo, 'Hiragino Sans', Montserrat, Helvetica, Arial, sans-serif"

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

        # Primary and sliding double-buffer frames
        self.frame_main = LyricsFrame(self)
        self.frame_slide = LyricsFrame(self)
        self.frame_slide.hide()

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
        self.frame_main.setGeometry(0, 0, width, height)
        self.frame_slide.setGeometry(0, 0, width, height)

        self.frame_main.apply_style(font_size, text_color, context_mode)
        self.frame_slide.apply_style(font_size, text_color, context_mode)

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

    def setLyrics(self, prev_line: str, curr_line: str, next_line: str, animate: bool = True):
        # Ignore redundant updates
        if curr_line == self._current_text:
            return

        old_curr = self._current_text
        self._current_text = curr_line
        trans_mode = self.config.get("transition_mode", "float")

        # Instant mode, cold start, or explicit non-animated update
        if not animate or trans_mode == "instant" or not old_curr:
            self._apply_instant(prev_line, curr_line, next_line)
            return

        # Stop active animation and finalize state before starting next
        if self.anim_group and self.anim_group.state() == QParallelAnimationGroup.State.Running:
            self.anim_group.stop()
            self._finalize_transition(self._pending_prev, self._pending_curr, self._pending_next)

        self._pending_prev = prev_line
        self._pending_curr = curr_line
        self._pending_next = next_line

        context_mode = self.config.get("context_mode", "next_only")
        font_size = self.config.get("font_size", 24)

        # Calculate exact vertical floating distance
        if context_mode == "next_only":
            delta = self.frame_main.lbl_next.y() - self.frame_main.lbl_curr.y()
            if delta <= 10:
                delta = max(35, int(font_size * 1.5))
            self.frame_main.lbl_next.setText("")
            self.frame_slide.lbl_prev.setText("")
            self.frame_slide.lbl_curr.setText(curr_line)
            self.frame_slide.lbl_next.setText(next_line)
        elif context_mode == "both":
            delta = self.frame_main.lbl_curr.y() - self.frame_main.lbl_prev.y()
            if delta <= 10:
                delta = max(35, int(font_size * 1.5))
            self.frame_main.lbl_next.setText("")
            self.frame_slide.lbl_prev.setText("")
            self.frame_slide.lbl_curr.setText(curr_line)
            self.frame_slide.lbl_next.setText(next_line)
        else:  # "none"
            delta = max(35, int(font_size * 1.4))
            self.frame_slide.lbl_curr.setText(curr_line)

        # Setup slide frame starting position
        self.frame_slide.move(0, delta)
        self.frame_slide.op_effect.setOpacity(0.2)
        self.frame_slide.show()

        # Parallel animation: smooth upward float + gentle fade
        self.anim_group = QParallelAnimationGroup(self)

        a_main_pos = QPropertyAnimation(self.frame_main, b"pos")
        a_main_pos.setDuration(380)
        a_main_pos.setStartValue(QPoint(0, 0))
        a_main_pos.setEndValue(QPoint(0, -delta))
        a_main_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

        a_main_op = QPropertyAnimation(self.frame_main.op_effect, b"opacity")
        a_main_op.setDuration(380)
        a_main_op.setStartValue(1.0)
        a_main_op.setEndValue(0.0)

        a_slide_pos = QPropertyAnimation(self.frame_slide, b"pos")
        a_slide_pos.setDuration(380)
        a_slide_pos.setStartValue(QPoint(0, delta))
        a_slide_pos.setEndValue(QPoint(0, 0))
        a_slide_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

        a_slide_op = QPropertyAnimation(self.frame_slide.op_effect, b"opacity")
        a_slide_op.setDuration(380)
        a_slide_op.setStartValue(0.2)
        a_slide_op.setEndValue(1.0)

        self.anim_group.addAnimation(a_main_pos)
        self.anim_group.addAnimation(a_main_op)
        self.anim_group.addAnimation(a_slide_pos)
        self.anim_group.addAnimation(a_slide_op)

        self.anim_group.finished.connect(lambda: self._finalize_transition(prev_line, curr_line, next_line))
        self.anim_group.start()

    def _finalize_transition(self, prev_line: str, curr_line: str, next_line: str):
        self.frame_main.lbl_prev.setText(prev_line)
        self.frame_main.lbl_curr.setText(curr_line)
        self.frame_main.lbl_next.setText(next_line)
        self.frame_main.move(0, 0)
        self.frame_main.op_effect.setOpacity(1.0)
        self.frame_slide.hide()
        self.frame_slide.move(0, 0)

    def _apply_instant(self, prev_line: str, curr_line: str, next_line: str):
        self.frame_main.lbl_prev.setText(prev_line)
        self.frame_main.lbl_curr.setText(curr_line)
        self.frame_main.lbl_next.setText(next_line)
        self.frame_main.move(0, 0)
        self.frame_main.op_effect.setOpacity(1.0)
        self.frame_slide.hide()

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
