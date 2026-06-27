"""
WordWidget: A custom QWidget that displays a single character with its
Jyutping annotation above it. Supports polyphonic character click menus.
Handles both CJK characters and grouped English word tokens.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QMenu, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize, QPointF
from PySide6.QtGui import QFont, QCursor, QFontMetrics, QPainter, QPen

from core.converter import LyricsToken
from core.tone_marks import TONE_LINE_LEVELS, split_tone
from ui.styles import COLORS, WORD_WIDGET_NORMAL, WORD_WIDGET_POLYPHONIC, SPACING_MODES, FONTS


class ToneMarkLabel(QLabel):
    """QLabel that can draw Jyutping tone numbers as corner tone-line marks."""

    def __init__(self, text: str = "", parent=None, tone_marks_enabled: bool = False):
        super().__init__(text, parent)
        self._tone_marks_enabled = tone_marks_enabled

    def set_tone_marks_enabled(self, enabled: bool):
        self._tone_marks_enabled = enabled
        self.update()

    def paintEvent(self, event):
        parts = split_tone(self.text()) if self._tone_marks_enabled else None
        if not parts:
            super().paintEvent(event)
            return

        base, tone = parts
        line_levels = TONE_LINE_LEVELS.get(tone)
        if not line_levels:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        color = self.palette().color(self.foregroundRole())
        base_font = self.font()
        base_metrics = QFontMetrics(base_font)
        digit_font = self._scaled_font(base_font, 0.72)
        digit_metrics = QFontMetrics(digit_font)

        base_width = base_metrics.horizontalAdvance(base)
        digit_width = digit_metrics.horizontalAdvance(tone)
        mark_width = max(4, int(digit_metrics.height() * 0.58))
        gap = max(1, int(base_metrics.height() * 0.06))
        group_width = base_width + gap + mark_width + gap + digit_width

        rect = self.contentsRect()
        x = rect.x() + (rect.width() - group_width) / 2
        base_y = rect.y() + (rect.height() - base_metrics.height()) / 2 + base_metrics.ascent()

        painter.setPen(color)
        painter.setFont(base_font)
        painter.drawText(int(round(x)), int(round(base_y)), base)

        mark_x1 = x + base_width + gap
        mark_x2 = mark_x1 + mark_width
        digit_x = mark_x2 + gap

        sup_top = max(rect.y(), base_y - base_metrics.ascent())
        tone_levels = {
            "top": sup_top + digit_metrics.height() * 0.12,
            "middle": sup_top + digit_metrics.height() * 0.45,
            "bottom": sup_top + digit_metrics.height() * 0.78,
        }
        y1 = tone_levels[line_levels[0]]
        y2 = tone_levels[line_levels[1]]

        pen = QPen(color)
        pen.setWidthF(max(1.0, base_metrics.height() * 0.08))
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(mark_x1, y1), QPointF(mark_x2, y2))

        painter.setPen(color)
        painter.setFont(digit_font)
        digit_y = sup_top + digit_metrics.ascent()
        painter.drawText(int(round(digit_x)), int(round(digit_y)), tone)

    def _scaled_font(self, font: QFont, factor: float) -> QFont:
        scaled = QFont(font)
        if scaled.pointSizeF() > 0:
            scaled.setPointSizeF(max(1.0, scaled.pointSizeF() * factor))
        elif scaled.pixelSize() > 0:
            scaled.setPixelSize(max(1, int(scaled.pixelSize() * factor)))
        return scaled


class WordWidget(QWidget):
    """
    Displays a single lyrics token: Jyutping on top, Chinese character below.
    Polyphonic characters are highlighted and clickable.
    Properly handles multi-char English word tokens.
    """

    jyutping_changed = Signal(int, str)  # (token_index, new_jyutping)

    def __init__(
        self,
        token: LyricsToken,
        parent=None,
        spacing_mode: str = "wide",
        font_mode: str = "apple",
        tone_marks_enabled: bool = False,
    ):
        super().__init__(parent)
        self.token = token
        self._spacing_mode = spacing_mode
        self._font_mode = font_mode
        self._tone_marks_enabled = tone_marks_enabled
        self.setObjectName("word_widget")
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        """Build the vertical layout: jyutping label on top, character below."""
        mode = SPACING_MODES[self._spacing_mode]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            mode['cell_margin_h'], mode['cell_margin_v'],
            mode['cell_margin_h'], mode['cell_margin_v']
        )
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        jyutping_font = QFont("Arial", mode['jyutping_pt'])
        char_font = QFont()
        if self._font_mode == "stzhongsong" and not self.token.char.isascii():
            char_font.setFamily("STZhongsong")
        elif self.token.char.isascii() and any(c.isalpha() for c in self.token.char):
            char_font.setFamily("Arial")
        else:
            char_font.setFamily(FONTS['family'])
        char_font.setPointSize(mode['char_pt'])

        if self.token.is_punctuation:
            # Punctuation / English word: show only the character, no Jyutping
            self._jyutping_label = QLabel("")
            self._jyutping_label.setFixedHeight(
                QFontMetrics(jyutping_font).height()
            )

            self._char_label = QLabel(self.token.char)
            self._char_label.setFont(char_font)
            self._char_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._char_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        else:
            # Jyutping label (small, on top, narrow Latin font)
            self._jyutping_label = ToneMarkLabel(
                self.token.current_jyutping or "",
                tone_marks_enabled=self._tone_marks_enabled
            )
            self._jyutping_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            j_font = QFont("Arial")
            j_font.setPointSize(mode['jyutping_pt'])
            j_font.setBold(True)
            self._jyutping_label.setFont(j_font)

            # Chinese character label
            self._char_label = QLabel(self.token.char)
            self._char_label.setFont(char_font)
            self._char_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            char_color = COLORS['text_secondary'] if self.token.char.isascii() else COLORS['text_primary']
            self._char_label.setStyleSheet(f"color: {char_color};")

            # Color the Jyutping label
            if self.token.is_polyphonic:
                self._jyutping_label.setStyleSheet(
                    f"color: {COLORS['polyphonic']}; font-weight: bold;"
                )
                self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                self.setToolTip(
                    f"多音字 — 点击选择读音\n"
                    f"候选: {', '.join(self.token.candidates)}"
                )
            else:
                self._jyutping_label.setStyleSheet(
                    f"color: {COLORS['accent_blue']};"
                )

        layout.addWidget(self._jyutping_label)
        layout.addWidget(self._char_label)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def _apply_style(self):
        """Apply the appropriate stylesheet based on polyphonic status."""
        if self.token.is_polyphonic:
            self.setStyleSheet(WORD_WIDGET_POLYPHONIC)
        else:
            self.setStyleSheet(WORD_WIDGET_NORMAL)

    def sizeHint(self) -> QSize:
        """Calculate the preferred size based on content."""
        mode = SPACING_MODES[self._spacing_mode]
        fixed_h = mode['widget_height']
        if self.token.char.isascii():
            # Narrower line height for English words (simulate 窄行距)
            fixed_h = int(mode['widget_height'] * 0.7)

        if self.token.is_punctuation:
            char = self.token.char
            if char in ('\n', '\r', '\r\n'):
                return QSize(0, 0)
            # For English words or punctuation, measure actual text width
            fm = QFontMetrics(self._char_label.font())
            text_w = fm.horizontalAdvance(char) + mode['cell_margin_h'] * 2 + 4
            # Spaces get a proper visible width
            if char.strip() == "":
                base_w = 16 if self._spacing_mode == "wide" else 10
                return QSize(base_w * max(1, len(char)), fixed_h)
            
            # Very small padding for English/Punctuation to avoid huge gaps
            text_w = fm.horizontalAdvance(char) + 2
            return QSize(text_w, fixed_h)

        # For CJK characters, width based on max of Jyutping and character
        jp_text = self.token.current_jyutping or ""
        jp_fm = QFontMetrics(self._jyutping_label.font())
        jp_w = jp_fm.horizontalAdvance(jp_text)

        char_fm = QFontMetrics(self._char_label.font())
        char_w = char_fm.horizontalAdvance(self.token.char)

        width = max(jp_w, char_w) + mode['cell_margin_h'] * 2 + 4
        return QSize(width, fixed_h)

    def mousePressEvent(self, event):
        """Show polyphonic candidate menu on click."""
        if (self.token.is_polyphonic
                and event.button() == Qt.MouseButton.LeftButton
                and self.token.candidates):
            self._show_candidates_menu(event.globalPosition().toPoint())
        super().mousePressEvent(event)

    def _show_candidates_menu(self, global_pos):
        """Display a popup menu with all Jyutping candidates."""
        menu = QMenu(self)
        menu.setObjectName("candidates_menu")

        # Add a header
        header = menu.addAction(f"「{self.token.char}」的读音")
        header.setEnabled(False)
        header_font = QFont()
        header_font.setBold(True)
        header.setFont(header_font)

        menu.addSeparator()

        for candidate in self.token.candidates:
            if candidate == self.token.current_jyutping:
                action = menu.addAction(f"✓  {candidate}")
                action_font = QFont()
                action_font.setBold(True)
                action.setFont(action_font)
            else:
                action = menu.addAction(f"    {candidate}")
            action.setData(candidate)

        chosen_action = menu.exec(global_pos)
        if chosen_action and chosen_action.data():
            new_jyutping = chosen_action.data()
            if new_jyutping != self.token.current_jyutping:
                self._update_jyutping(new_jyutping)

    def _update_jyutping(self, new_jyutping: str):
        """Update the displayed Jyutping and emit change signal."""
        self.token.current_jyutping = new_jyutping
        self._jyutping_label.setText(new_jyutping)
        self.updateGeometry()
        self.jyutping_changed.emit(self.token.index, new_jyutping)


class LineBreakWidget(QWidget):
    """
    Invisible widget that signals the FlowLayout to break to a new line.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("is_line_break", True)
        self.setFixedSize(0, 0)
        self.hide()
