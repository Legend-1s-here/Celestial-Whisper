import sys
import os
import webbrowser
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QSlider,
    QCheckBox, QTabWidget, QWidget, QFrame, QMessageBox,
    QColorDialog
)
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap

BG_IMAGE_PATH = Path(__file__).parent / "japanese_bg.jpg"

class SettingsDialog(QDialog):
    settings_saved = pyqtSignal(dict)
    test_lyrics_requested = pyqtSignal()

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = dict(config)
        self.setWindowTitle("🌸 Celestial Whisper — 設定 (Settings)")
        self.setFixedSize(650, 720)

        self.bg_pixmap = None
        if BG_IMAGE_PATH.exists():
            self.bg_pixmap = QPixmap(str(BG_IMAGE_PATH))

        self.setStyleSheet("""
            QDialog {
                background-color: #12131D;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Meiryo', 'Hiragino Sans', sans-serif;
            }
            QLabel {
                color: #F0F0F8;
                font-size: 10pt;
                background: transparent;
            }
            QLineEdit {
                background-color: rgba(22, 24, 38, 0.92);
                border: 1px solid rgba(255, 183, 197, 0.35);
                border-radius: 6px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 10pt;
                min-height: 24px;
            }
            QLineEdit:focus {
                border: 1.5px solid #FF8DA1;
                background-color: rgba(30, 32, 50, 0.98);
            }
            QTabWidget::pane {
                border: 1px solid rgba(255, 183, 197, 0.3);
                border-radius: 10px;
                background: rgba(18, 20, 32, 0.88);
                top: -1px;
            }
            QTabBar::tab {
                background: rgba(22, 24, 38, 0.8);
                color: #B5B8CD;
                padding: 10px 22px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                font-size: 10pt;
                margin-right: 6px;
                border: 1px solid rgba(255, 183, 197, 0.2);
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: rgba(36, 38, 58, 0.96);
                color: #FFB7C5;
                border-top: 2.5px solid #FF8DA1;
                border-left: 1px solid rgba(255, 183, 197, 0.4);
                border-right: 1px solid rgba(255, 183, 197, 0.4);
            }
            QPushButton {
                background-color: rgba(35, 38, 58, 0.92);
                color: #FFFFFF;
                border: 1px solid rgba(255, 183, 197, 0.35);
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: 600;
                font-size: 9.5pt;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: rgba(54, 58, 88, 0.98);
                border-color: #FFB7C5;
            }
            QPushButton#primaryBtn {
                background-color: #FF8DA1;
                color: #121218;
                border: none;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton#primaryBtn:hover {
                background-color: #FFA5B6;
            }
            QPushButton#testBtn {
                background-color: rgba(79, 70, 229, 0.85);
                color: #FFFFFF;
                border: 1px solid rgba(165, 180, 252, 0.4);
            }
            QPushButton#testBtn:hover {
                background-color: rgba(99, 102, 241, 0.95);
            }
            QRadioButton {
                color: #F0F0F8;
                font-size: 10pt;
                spacing: 12px;
                background: transparent;
                padding: 3px 0px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #A5A8BD;
                background-color: rgba(26, 28, 44, 0.9);
            }
            QRadioButton::indicator:checked {
                border: 2px solid #FF8DA1;
                background-color: #FF8DA1;
            }
            QRadioButton::indicator:hover {
                border-color: #FFB7C5;
            }
            QCheckBox {
                color: #F0F0F8;
                font-size: 10pt;
                spacing: 12px;
                background: transparent;
                padding: 4px 0px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #A5A8BD;
                background-color: rgba(26, 28, 44, 0.9);
            }
            QCheckBox::indicator:checked {
                border: 2px solid #FF8DA1;
                background-color: #FF8DA1;
            }
            QCheckBox::indicator:hover {
                border-color: #FFB7C5;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: rgba(45, 48, 70, 0.85);
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #FF8DA1;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                border: 2px solid #FF8DA1;
                width: 16px;
                margin-top: -6px;
                margin-bottom: -6px;
                border-radius: 9px;
            }
        """)

        self._build_ui()
        self._load_values()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.bg_pixmap and not self.bg_pixmap.isNull():
            scaled = self.bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            painter.drawPixmap(0, 0, scaled, x, y, self.width(), self.height())
            painter.fillRect(self.rect(), QColor(14, 16, 26, 205))
        else:
            painter.fillRect(self.rect(), QColor(18, 19, 29))

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 18, 24, 18)
        main_layout.setSpacing(12)

        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title_label = QLabel("🌸 桜 Celestial Whisper • 設定")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #FFFFFF;")
        title_box.addWidget(title_label)

        subtitle_label = QLabel("Spotify 浮動歌詞オーバーレイ • Floating Subtitles")
        subtitle_label.setStyleSheet("font-size: 9pt; color: #FFB7C5; font-weight: 500;")
        title_box.addWidget(subtitle_label)

        header_layout.addLayout(title_box)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_spotify_tab(), "🎵 再生設定 (Playback)")
        self.tabs.addTab(self._create_appearance_tab(), "🌸 位置 ＆ スタイル (Position ＆ Style)")
        main_layout.addWidget(self.tabs)

        btn_layout = QHBoxLayout()

        self.btn_test = QPushButton("▶ Test Floating Lyrics")
        self.btn_test.setObjectName("testBtn")
        self.btn_test.clicked.connect(self._on_test_clicked)
        btn_layout.addWidget(self.btn_test)

        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Save && Apply")
        self.btn_save.setObjectName("primaryBtn")
        self.btn_save.clicked.connect(self._save_and_close)
        btn_layout.addWidget(self.btn_save)

        main_layout.addLayout(btn_layout)

    def _create_spotify_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        info_box = QFrame()
        info_box.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 28, 44, 0.88);
                border: 1px solid rgba(255, 183, 197, 0.28);
                border-radius: 8px;
            }
        """)
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(16, 16, 16, 16)
        info_layout.setSpacing(10)

        info_title = QLabel("✨ Native Windows Media Mode (Active)")
        info_title.setStyleSheet("font-weight: bold; color: #1DB954; font-size: 11pt;")
        info_layout.addWidget(info_title)

        guide_label = QLabel()
        guide_label.setTextFormat(Qt.TextFormat.RichText)
        guide_label.setText(
            "<b>No Spotify Premium or API Keys Required!</b><br>"
            "Celestial Whisper captures playback directly from Windows. It works out-of-the-box for "
            "<span style='color:#FFB7C5;'><b>Spotify Free, Spotify Premium, Desktop & Web</b></span>.<br><br>"
            "<i>(Optional) If you have a Spotify Developer App with Premium, you can enter credentials below:</i>"
        )
        guide_label.setStyleSheet("color: #E2E4F0; font-size: 9.5pt; line-height: 1.5;")
        guide_label.setWordWrap(True)
        info_layout.addWidget(guide_label)

        layout.addWidget(info_box)

        lbl_id = QLabel("Spotify Client ID (Optional):")
        lbl_id.setStyleSheet("font-weight: 600; color: #F0F0F8;")
        layout.addWidget(lbl_id)
        self.input_client_id = QLineEdit()
        self.input_client_id.setPlaceholderText("Leave empty for Free mode")
        layout.addWidget(self.input_client_id)

        lbl_sec = QLabel("Spotify Client Secret (Optional):")
        lbl_sec.setStyleSheet("font-weight: 600; color: #F0F0F8;")
        layout.addWidget(lbl_sec)
        self.input_client_secret = QLineEdit()
        self.input_client_secret.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_client_secret.setPlaceholderText("Leave empty for Free mode")
        layout.addWidget(self.input_client_secret)

        lbl_uri = QLabel("Redirect URI:")
        lbl_uri.setStyleSheet("font-weight: 600; color: #F0F0F8;")
        layout.addWidget(lbl_uri)
        self.input_redirect_uri = QLineEdit()
        self.input_redirect_uri.setText("http://127.0.0.1:8888/callback")
        layout.addWidget(self.input_redirect_uri)

        layout.addStretch()
        return tab

    def _create_appearance_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # 1. Position Card
        pos_box = QFrame()
        pos_box.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 28, 44, 0.88);
                border: 1px solid rgba(255, 183, 197, 0.28);
                border-radius: 8px;
            }
        """)
        pos_layout = QVBoxLayout(pos_box)
        pos_layout.setContentsMargins(14, 10, 14, 10)
        pos_layout.setSpacing(6)

        lbl_pos_title = QLabel("📍 Overlay Position on Screen")
        lbl_pos_title.setStyleSheet("font-weight: bold; color: #FFB7C5; font-size: 10pt;")
        pos_layout.addWidget(lbl_pos_title)

        self.radio_top = QRadioButton("Top of Screen (floating above windows/games)")
        self.radio_bottom = QRadioButton("Bottom Center (classic subtitle style)")

        self.pos_group = QButtonGroup(self)
        self.pos_group.addButton(self.radio_top)
        self.pos_group.addButton(self.radio_bottom)

        pos_layout.addWidget(self.radio_top)
        pos_layout.addWidget(self.radio_bottom)
        layout.addWidget(pos_box)

        # 2. Context Lines Mode Card (NEW: Option for Only Next Lyrics!)
        ctx_box = QFrame()
        ctx_box.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 28, 44, 0.88);
                border: 1px solid rgba(255, 183, 197, 0.28);
                border-radius: 8px;
            }
        """)
        ctx_layout = QVBoxLayout(ctx_box)
        ctx_layout.setContentsMargins(14, 10, 14, 10)
        ctx_layout.setSpacing(6)

        lbl_ctx_title = QLabel("📜 Lyrics Lines Display")
        lbl_ctx_title.setStyleSheet("font-weight: bold; color: #FFB7C5; font-size: 10pt;")
        ctx_layout.addWidget(lbl_ctx_title)

        self.radio_next_only = QRadioButton("Next Lyric Only (Current + Upcoming line, no previous)")
        self.radio_both = QRadioButton("Both Previous and Next Lyrics (3 lines total)")
        self.radio_none = QRadioButton("Current Lyric Only (1 line)")

        self.ctx_group = QButtonGroup(self)
        self.ctx_group.addButton(self.radio_next_only)
        self.ctx_group.addButton(self.radio_both)
        self.ctx_group.addButton(self.radio_none)

        ctx_layout.addWidget(self.radio_next_only)
        ctx_layout.addWidget(self.radio_both)
        ctx_layout.addWidget(self.radio_none)
        layout.addWidget(ctx_box)

        # 3. Width & Font Size Sliders Card
        size_box = QFrame()
        size_box.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 28, 44, 0.88);
                border: 1px solid rgba(255, 183, 197, 0.28);
                border-radius: 8px;
            }
        """)
        size_layout = QVBoxLayout(size_box)
        size_layout.setContentsMargins(14, 10, 14, 10)
        size_layout.setSpacing(8)

        # Width slider
        self.lbl_width_val = QLabel("Overlay Width: 1400 px")
        self.lbl_width_val.setStyleSheet("font-weight: bold; color: #FFB7C5; font-size: 9.5pt;")
        size_layout.addWidget(self.lbl_width_val)

        self.slider_width = QSlider(Qt.Orientation.Horizontal)
        self.slider_width.setRange(1000, 1800)
        self.slider_width.setSingleStep(50)
        self.slider_width.setValue(1400)
        self.slider_width.valueChanged.connect(self._on_width_slider_changed)
        size_layout.addWidget(self.slider_width)

        # Font size slider
        self.lbl_size_val = QLabel("Font Size: 26 pt")
        self.lbl_size_val.setStyleSheet("font-weight: bold; color: #FFB7C5; font-size: 9.5pt;")
        size_layout.addWidget(self.lbl_size_val)

        self.slider_size = QSlider(Qt.Orientation.Horizontal)
        self.slider_size.setRange(16, 44)
        self.slider_size.setValue(26)
        self.slider_size.valueChanged.connect(self._on_size_slider_changed)
        size_layout.addWidget(self.slider_size)

        layout.addWidget(size_box)

        # 4. Active Lyric Color Card
        color_box = QFrame()
        color_box.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 28, 44, 0.88);
                border: 1px solid rgba(255, 183, 197, 0.28);
                border-radius: 8px;
            }
        """)
        color_layout = QHBoxLayout(color_box)
        color_layout.setContentsMargins(14, 8, 14, 8)
        color_layout.setSpacing(10)

        lbl_color = QLabel("Active Lyric Color:")
        lbl_color.setStyleSheet("font-weight: bold; color: #FFB7C5;")
        color_layout.addWidget(lbl_color)

        self.current_color = self.config.get("text_color", "#FFFFFF")
        self.color_preview = QPushButton()
        self.color_preview.setFixedSize(46, 26)
        self._update_color_preview_btn()
        self.color_preview.clicked.connect(self._choose_color)
        color_layout.addWidget(self.color_preview)

        presets = [
            ("#FFFFFF", "White"),
            ("#FFB7C5", "Sakura Pink"),
            ("#1DB954", "Spotify"),
            ("#00F5D4", "Cyan"),
            ("#FFD166", "Gold")
        ]
        for hex_val, name in presets:
            btn = QPushButton(name)
            btn.setStyleSheet(f"""
                background-color: {hex_val};
                color: #121218;
                font-size: 8.5pt;
                font-weight: bold;
                padding: 3px 8px;
                border: 1px solid rgba(0,0,0,0.25);
            """)
            btn.clicked.connect(lambda checked, h=hex_val: self._set_color_preset(h))
            color_layout.addWidget(btn)

        color_layout.addStretch()
        layout.addWidget(color_box)

        # 5. Lock Checkbox Card
        chk_box = QFrame()
        chk_box.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 28, 44, 0.88);
                border: 1px solid rgba(255, 183, 197, 0.28);
                border-radius: 8px;
            }
        """)
        chk_layout = QVBoxLayout(chk_box)
        chk_layout.setContentsMargins(14, 8, 14, 8)
        chk_layout.setSpacing(4)

        self.chk_lock = QCheckBox("Lock position (prevent accidental mouse dragging)")
        chk_layout.addWidget(self.chk_lock)
        layout.addWidget(chk_box)

        layout.addStretch()
        return tab

    def _on_width_slider_changed(self, value):
        self.lbl_width_val.setText(f"Overlay Width: {value} px")

    def _on_size_slider_changed(self, value):
        self.lbl_size_val.setText(f"Font Size: {value} pt")

    def _choose_color(self):
        col = QColorDialog.getColor(QColor(self.current_color), self, "Select Active Lyric Color")
        if col.isValid():
            self.current_color = col.name()
            self._update_color_preview_btn()

    def _set_color_preset(self, hex_val: str):
        self.current_color = hex_val
        self._update_color_preview_btn()

    def _update_color_preview_btn(self):
        self.color_preview.setStyleSheet(f"""
            background-color: {self.current_color};
            border: 2px solid #FFFFFF;
            border-radius: 4px;
        """)

    def _load_values(self):
        self.input_client_id.setText(self.config.get("spotify_client_id", ""))
        self.input_client_secret.setText(self.config.get("spotify_client_secret", ""))
        self.input_redirect_uri.setText(self.config.get("spotify_redirect_uri", "http://127.0.0.1:8888/callback"))

        pos = self.config.get("position", "bottom")
        if pos == "top":
            self.radio_top.setChecked(True)
        else:
            self.radio_bottom.setChecked(True)

        # Load context mode
        ctx_mode = self.config.get("context_mode", "next_only")
        if ctx_mode == "next_only":
            self.radio_next_only.setChecked(True)
        elif ctx_mode == "none":
            self.radio_none.setChecked(True)
        else:
            self.radio_both.setChecked(True)

        width = self.config.get("window_width", 1400)
        self.slider_width.setValue(width)
        self.lbl_width_val.setText(f"Overlay Width: {width} px")

        size = self.config.get("font_size", 26)
        self.slider_size.setValue(size)
        self.lbl_size_val.setText(f"Font Size: {size} pt")

        self.chk_lock.setChecked(self.config.get("lock_position", False))

    def _on_test_clicked(self):
        self._gather_into_config()
        self.test_lyrics_requested.emit()

    def _gather_into_config(self):
        self.config["spotify_client_id"] = self.input_client_id.text().strip()
        self.config["spotify_client_secret"] = self.input_client_secret.text().strip()
        self.config["spotify_redirect_uri"] = self.input_redirect_uri.text().strip() or "http://127.0.0.1:8888/callback"
        self.config["position"] = "top" if self.radio_top.isChecked() else "bottom"

        if self.radio_next_only.isChecked():
            self.config["context_mode"] = "next_only"
        elif self.radio_none.isChecked():
            self.config["context_mode"] = "none"
        else:
            self.config["context_mode"] = "both"

        self.config["window_width"] = self.slider_width.value()
        self.config["font_size"] = self.slider_size.value()
        self.config["text_color"] = self.current_color
        self.config["lock_position"] = self.chk_lock.isChecked()

    def _save_and_close(self):
        self._gather_into_config()
        self.settings_saved.emit(self.config)
        self.accept()
