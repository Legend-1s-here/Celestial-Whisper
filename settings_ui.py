import sys
import os
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QSlider,
    QCheckBox, QWidget, QFrame, QColorDialog
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
        self.setFixedSize(600, 840)

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
            painter.fillRect(self.rect(), QColor(14, 16, 26, 210))
        else:
            painter.fillRect(self.rect(), QColor(18, 19, 29))

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(22, 16, 22, 16)
        main_layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title_label = QLabel("🌸 桜 Celestial Whisper • 設定")
        title_label.setStyleSheet("font-size: 13.5pt; font-weight: bold; color: #FFFFFF;")
        title_box.addWidget(title_label)

        subtitle_label = QLabel("Spotify 浮動歌詞オーバーレイ • Floating Subtitles")
        subtitle_label.setStyleSheet("font-size: 9pt; color: #FFB7C5; font-weight: 500;")
        title_box.addWidget(subtitle_label)

        header_layout.addLayout(title_box)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Status badge
        status_box = QFrame()
        status_box.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 28, 44, 0.88);
                border: 1px solid rgba(29, 185, 84, 0.4);
                border-radius: 8px;
            }
        """)
        status_layout = QHBoxLayout(status_box)
        status_layout.setContentsMargins(14, 8, 14, 8)
        status_layout.setSpacing(8)

        badge = QLabel("🟢 Native Auto-Detect Active")
        badge.setStyleSheet("font-weight: bold; color: #1DB954; font-size: 9.5pt;")
        status_layout.addWidget(badge)

        desc = QLabel("Captures playback automatically. No login or API keys needed!")
        desc.setStyleSheet("color: #B5B8CD; font-size: 8.5pt;")
        status_layout.addWidget(desc)
        status_layout.addStretch()

        main_layout.addWidget(status_box)

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
        pos_layout.setContentsMargins(14, 8, 14, 8)
        pos_layout.setSpacing(4)

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
        main_layout.addWidget(pos_box)

        # 2. English / Language Mode Card (User specified: English letters / Hinglish!)
        lang_box = QFrame()
        lang_box.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 28, 44, 0.88);
                border: 1px solid rgba(255, 183, 197, 0.28);
                border-radius: 8px;
            }
        """)
        lang_layout = QVBoxLayout(lang_box)
        lang_layout.setContentsMargins(14, 8, 14, 8)
        lang_layout.setSpacing(4)

        lbl_lang_title = QLabel("🌐 Lyrics Script / Language")
        lbl_lang_title.setStyleSheet("font-weight: bold; color: #FFB7C5; font-size: 10pt;")
        lang_layout.addWidget(lbl_lang_title)

        self.radio_lang_romanized = QRadioButton("English Letters / Hinglish (e.g. \"Yaad aati nahi\", Romaji)")
        self.radio_lang_translation = QRadioButton("English Meaning (Translate foreign words to English)")
        self.radio_lang_original = QRadioButton("Original Native Script (Devanagari, Kanji, etc.)")

        self.lang_group = QButtonGroup(self)
        self.lang_group.addButton(self.radio_lang_romanized)
        self.lang_group.addButton(self.radio_lang_translation)
        self.lang_group.addButton(self.radio_lang_original)

        lang_layout.addWidget(self.radio_lang_romanized)
        lang_layout.addWidget(self.radio_lang_translation)
        lang_layout.addWidget(self.radio_lang_original)
        main_layout.addWidget(lang_box)

        # 3. Lyrics Display Mode Card
        ctx_box = QFrame()
        ctx_box.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 28, 44, 0.88);
                border: 1px solid rgba(255, 183, 197, 0.28);
                border-radius: 8px;
            }
        """)
        ctx_layout = QVBoxLayout(ctx_box)
        ctx_layout.setContentsMargins(14, 8, 14, 8)
        ctx_layout.setSpacing(4)

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
        main_layout.addWidget(ctx_box)

        # 4. Lyric Transition Style Card (Float vs Pop)
        trans_box = QFrame()
        trans_box.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 28, 44, 0.88);
                border: 1px solid rgba(255, 183, 197, 0.28);
                border-radius: 8px;
            }
        """)
        trans_layout = QVBoxLayout(trans_box)
        trans_layout.setContentsMargins(14, 8, 14, 8)
        trans_layout.setSpacing(4)

        lbl_trans_title = QLabel("🌸 Lyric Transition Animation (Float vs Pop)")
        lbl_trans_title.setStyleSheet("font-weight: bold; color: #FFB7C5; font-size: 10pt;")
        trans_layout.addWidget(lbl_trans_title)

        self.radio_trans_float = QRadioButton("Smooth Float Up (Lyrics glide && float upwards smoothly — easy to read)")
        self.radio_trans_instant = QRadioButton("Instant Pop (Classic abrupt text switch without motion)")

        self.trans_group = QButtonGroup(self)
        self.trans_group.addButton(self.radio_trans_float)
        self.trans_group.addButton(self.radio_trans_instant)

        trans_layout.addWidget(self.radio_trans_float)
        trans_layout.addWidget(self.radio_trans_instant)
        main_layout.addWidget(trans_box)

        # 4. Gaming & Fullscreen Card
        game_box = QFrame()
        game_box.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 28, 44, 0.88);
                border: 1px solid rgba(255, 183, 197, 0.28);
                border-radius: 8px;
            }
        """)
        game_layout = QVBoxLayout(game_box)
        game_layout.setContentsMargins(14, 8, 14, 8)
        game_layout.setSpacing(4)

        lbl_game_title = QLabel("🎮 Gaming & Fullscreen Mode")
        lbl_game_title.setStyleSheet("font-weight: bold; color: #FFB7C5; font-size: 10pt;")
        game_layout.addWidget(lbl_game_title)

        self.chk_click_through = QCheckBox("Game Mode: Pass mouse clicks through overlay to game (Click-Through)")
        self.chk_click_through.setStyleSheet("color: #FFFFFF; font-size: 9pt;")
        game_layout.addWidget(self.chk_click_through)

        lbl_game_tip = QLabel("💡 Tip: For games to show desktop overlays, set your game video mode to 'Borderless Windowed' or 'Windowed Fullscreen'.")
        lbl_game_tip.setStyleSheet("color: #9EA2B8; font-size: 8pt; font-style: italic;")
        lbl_game_tip.setWordWrap(True)
        game_layout.addWidget(lbl_game_tip)

        main_layout.addWidget(game_box)

        # 4. Width & Font Size Sliders Card
        size_box = QFrame()
        size_box.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 28, 44, 0.88);
                border: 1px solid rgba(255, 183, 197, 0.28);
                border-radius: 8px;
            }
        """)
        size_layout = QVBoxLayout(size_box)
        size_layout.setContentsMargins(14, 8, 14, 8)
        size_layout.setSpacing(6)

        self.lbl_width_val = QLabel("Overlay Width: 1400 px")
        self.lbl_width_val.setStyleSheet("font-weight: bold; color: #FFB7C5; font-size: 9.5pt;")
        size_layout.addWidget(self.lbl_width_val)

        self.slider_width = QSlider(Qt.Orientation.Horizontal)
        self.slider_width.setRange(1000, 1800)
        self.slider_width.setSingleStep(50)
        self.slider_width.setValue(1400)
        self.slider_width.valueChanged.connect(self._on_width_slider_changed)
        size_layout.addWidget(self.slider_width)

        self.lbl_size_val = QLabel("Font Size: 24 pt")
        self.lbl_size_val.setStyleSheet("font-weight: bold; color: #FFB7C5; font-size: 9.5pt;")
        size_layout.addWidget(self.lbl_size_val)

        self.slider_size = QSlider(Qt.Orientation.Horizontal)
        self.slider_size.setRange(16, 44)
        self.slider_size.setValue(24)
        self.slider_size.valueChanged.connect(self._on_size_slider_changed)
        size_layout.addWidget(self.slider_size)

        main_layout.addWidget(size_box)

        # 5. Active Lyric Color Card
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

        self.current_color = self.config.get("text_color", "#FFB7C5")
        self.color_preview = QPushButton()
        self.color_preview.setFixedSize(44, 26)
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
        main_layout.addWidget(color_box)

        # 6. Lock Checkbox Card
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
        main_layout.addWidget(chk_box)

        # Bottom Buttons
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
        pos = self.config.get("position", "bottom")
        if pos == "top":
            self.radio_top.setChecked(True)
        else:
            self.radio_bottom.setChecked(True)

        lang_mode = self.config.get("language_mode", "romanized")
        if lang_mode == "translation":
            self.radio_lang_translation.setChecked(True)
        elif lang_mode == "original":
            self.radio_lang_original.setChecked(True)
        else:
            self.radio_lang_romanized.setChecked(True)

        ctx_mode = self.config.get("context_mode", "next_only")
        if ctx_mode == "next_only":
            self.radio_next_only.setChecked(True)
        elif ctx_mode == "none":
            self.radio_none.setChecked(True)
        else:
            self.radio_both.setChecked(True)

        trans_mode = self.config.get("transition_mode", "float")
        if trans_mode == "instant":
            self.radio_trans_instant.setChecked(True)
        else:
            self.radio_trans_float.setChecked(True)

        width = self.config.get("window_width", 1400)
        self.slider_width.setValue(width)
        self.lbl_width_val.setText(f"Overlay Width: {width} px")

        size = self.config.get("font_size", 24)
        self.slider_size.setValue(size)
        self.lbl_size_val.setText(f"Font Size: {size} pt")

        self.chk_lock.setChecked(self.config.get("lock_position", False))
        self.chk_click_through.setChecked(self.config.get("click_through", False))

    def _on_test_clicked(self):
        self._gather_into_config()
        self.test_lyrics_requested.emit()

    def _gather_into_config(self):
        self.config["position"] = "top" if self.radio_top.isChecked() else "bottom"

        if self.radio_lang_translation.isChecked():
            self.config["language_mode"] = "translation"
        elif self.radio_lang_original.isChecked():
            self.config["language_mode"] = "original"
        else:
            self.config["language_mode"] = "romanized"

        if self.radio_next_only.isChecked():
            self.config["context_mode"] = "next_only"
        elif self.radio_none.isChecked():
            self.config["context_mode"] = "none"
        else:
            self.config["context_mode"] = "both"

        self.config["transition_mode"] = "instant" if self.radio_trans_instant.isChecked() else "float"

        self.config["window_width"] = self.slider_width.value()
        self.config["font_size"] = self.slider_size.value()
        self.config["text_color"] = self.current_color
        self.config["lock_position"] = self.chk_lock.isChecked()
        self.config["click_through"] = self.chk_click_through.isChecked()

    def _save_and_close(self):
        self._gather_into_config()
        self.settings_saved.emit(self.config)
        self.accept()
