"""
Result Panel: Displays the converted lyrics with Jyutping annotations
using a FlowLayout of WordWidgets inside a QScrollArea.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from core.converter import LyricsToken
from ui.flow_layout import FlowLayout
from ui.word_widget import WordWidget, LineBreakWidget
from ui.styles import COLORS, SPACING_MODES


class ResultPanel(QWidget):
    """
    Bottom section of the main work area.
    Displays Jyutping-annotated lyrics in a scrollable flow layout.
    """

    token_changed = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tokens: list[LyricsToken] = []
        self._word_widgets: list[WordWidget] = []
        self._spacing_mode = "wide"
        self._font_mode = "apple"
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # ── Section Title ──
        title_row = QHBoxLayout()
        title_label = QLabel("🎵 转换结果")
        title_label.setObjectName("section_title")
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        title_label.setFont(font)
        title_row.addWidget(title_label)
        title_row.addStretch()

        self._stats_label = QLabel("")
        self._stats_label.setObjectName("section_subtitle")
        title_row.addWidget(self._stats_label)

        layout.addLayout(title_row)

        # ── Scroll Area with Flow Layout ──
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._flow_container = QWidget()
        self._flow_container.setStyleSheet(
            f"background-color: {COLORS['bg_card']}; border: none;"
        )
        mode = SPACING_MODES[self._spacing_mode]
        self._flow_layout = FlowLayout(
            self._flow_container,
            h_spacing=mode['widget_h_spacing'],
            v_spacing=mode['widget_v_spacing']
        )
        self._flow_layout.setContentsMargins(12, 12, 12, 12)

        self._scroll_area.setWidget(self._flow_container)
        layout.addWidget(self._scroll_area, stretch=1)

        # ── Empty state placeholder ──
        self._show_placeholder()

    def _show_placeholder(self):
        self._placeholder = QLabel(
            "转换结果将显示在此处\n\n"
            "请在上方输入歌词，然后点击「开始转换」"
        )
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 14px; padding: 50px;"
        )
        self._flow_layout.addWidget(self._placeholder)

    def set_spacing_mode(self, mode: str):
        """Update spacing mode and re-render if tokens exist."""
        if mode == self._spacing_mode:
            return
        self._spacing_mode = mode
        m = SPACING_MODES[mode]
        self._flow_layout._h_spacing = m['widget_h_spacing']
        self._flow_layout._v_spacing = m['widget_v_spacing']
        if self._tokens:
            self.render_tokens(self._tokens)

    def set_font_mode(self, mode: str):
        """Update font mode and re-render if tokens exist."""
        if mode == self._font_mode:
            return
        self._font_mode = mode
        if self._tokens:
            self.render_tokens(self._tokens)

    def render_tokens(self, tokens: list[LyricsToken]):
        """Render a list of LyricsToken objects as WordWidgets in the flow layout."""
        self._flow_layout.clear()
        self._word_widgets.clear()
        self._tokens = tokens

        if not tokens:
            self._show_placeholder()
            self._stats_label.setText("")
            return

        total_chars = 0
        polyphonic_count = 0

        for token in tokens:
            if token.is_punctuation and token.char in ('\n', '\r', '\r\n'):
                line_break = LineBreakWidget(self._flow_container)
                self._flow_layout.addWidget(line_break)
            else:
                ww = WordWidget(
                    token, self._flow_container,
                    spacing_mode=self._spacing_mode,
                    font_mode=self._font_mode
                )
                ww.jyutping_changed.connect(self._on_jyutping_changed)
                self._flow_layout.addWidget(ww)
                self._word_widgets.append(ww)

                if not token.is_punctuation:
                    total_chars += 1
                    if token.is_polyphonic:
                        polyphonic_count += 1

        self._stats_label.setText(
            f"共 {total_chars} 字 · {polyphonic_count} 个多音字"
        )

        self._flow_container.adjustSize()

    def _on_jyutping_changed(self, token_index: int, new_jyutping: str):
        for token in self._tokens:
            if token.index == token_index:
                token.current_jyutping = new_jyutping
                break
        self.token_changed.emit(token_index, new_jyutping)

    def get_tokens(self) -> list[LyricsToken]:
        return self._tokens

    def has_results(self) -> bool:
        return len(self._tokens) > 0
