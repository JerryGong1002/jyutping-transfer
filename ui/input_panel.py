"""
Input Panel: Contains the text editor for lyrics input and the action toolbar.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QLabel, QSizePolicy, QLineEdit, QCheckBox
)
from PySide6.QtCore import Signal, Qt, QSize, QRectF, QPointF
from PySide6.QtGui import QFont, QFontMetrics, QPainter, QPen, QColor

from ui.styles import COLORS, FONTS


class ToolbarCheckBox(QCheckBox):
    """Checkbox with a stable hand-drawn indicator for the compact toolbar."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)

    def sizeHint(self) -> QSize:
        metrics = QFontMetrics(self.font())
        width = 18 + 8 + metrics.horizontalAdvance(self.text()) + 8
        return QSize(width, max(36, metrics.height() + 12))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        box_size = 18
        box_x = 2
        box_y = (self.height() - box_size) / 2
        box_rect = QRectF(box_x, box_y, box_size, box_size)

        border = QColor(COLORS['accent_blue'] if self.isChecked() else COLORS['border'])
        fill = QColor("#eaf3ff" if self.isChecked() else COLORS['bg_card'])
        painter.setBrush(fill)
        painter.setPen(QPen(border, 1.4))
        painter.drawRoundedRect(box_rect, 3, 3)

        if self.isChecked():
            check_pen = QPen(QColor(COLORS['accent_blue']), 2.2)
            check_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            check_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(check_pen)
            painter.drawLine(
                QPointF(box_x + 4.5, box_y + 9.5),
                QPointF(box_x + 8.0, box_y + 13.0),
            )
            painter.drawLine(
                QPointF(box_x + 8.0, box_y + 13.0),
                QPointF(box_x + 14.0, box_y + 5.5),
            )

        text_color = COLORS['text_secondary'] if self.isEnabled() else COLORS['text_muted']
        painter.setPen(QColor(text_color))
        painter.setFont(self.font())
        metrics = QFontMetrics(self.font())
        text_x = box_x + box_size + 8
        text_y = (self.height() - metrics.height()) / 2 + metrics.ascent()
        painter.drawText(QPointF(text_x, text_y), self.text())


class InputPanel(QWidget):
    """
    Top section of the main work area.
    Contains a text editor for lyrics input and an action toolbar.
    """

    # Signals
    convert_requested = Signal(str, str)          # (text, cc_mode)
    favorite_requested = Signal()
    export_png_requested = Signal(str, float, str, bool)     # (font_mode, spacing, spacing_mode, tone_marks_enabled)
    export_pdf_requested = Signal(str, float, str, bool)
    spacing_mode_changed = Signal(str)            # "compact" or "wide"
    font_mode_changed = Signal(str)               # "apple" or "stzhongsong"
    tone_marks_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # ── Section Title ──
        title_row = QHBoxLayout()
        title_label = QLabel("📝 歌词输入")
        title_label.setObjectName("section_title")
        title_label.setFont(self._make_font(13, bold=True))
        title_row.addWidget(title_label)
        title_row.addStretch()

        self._char_count_label = QLabel("共 0 字")
        self._char_count_label.setObjectName("section_subtitle")
        title_row.addWidget(self._char_count_label)

        layout.addLayout(title_row)

        # ── Meta Info (Song Title / Artist) ──
        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("歌名/主题 (可选)")

        self._artist_input = QLineEdit()
        self._artist_input.setPlaceholderText("歌手 (可选)")

        meta_row.addWidget(self._title_input, stretch=3)
        meta_row.addWidget(self._artist_input, stretch=2)
        layout.addLayout(meta_row)

        # ── Text Editor ──
        self._text_edit = QTextEdit()
        self._text_edit.setPlaceholderText(
            "在此粘贴或输入粤语歌词...\n\n"
            "示例：\n"
            "风继续吹 不忍远离\n"
            "心里极渴望 希望留下伴着你"
        )
        self._text_edit.setMinimumHeight(120)
        self._text_edit.setFont(self._make_font(14))
        self._text_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._text_edit, stretch=1)

        # ── Action Toolbar ──
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)
        toolbar.setContentsMargins(0, 2, 0, 2)
        toolbar.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # CC mode dropdown
        cc_label = QLabel("繁简:")
        cc_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self._prepare_toolbar_label(cc_label)
        toolbar.addWidget(cc_label)

        self._cc_combo = QComboBox()
        self._cc_combo.addItem("不转换", "none")
        self._cc_combo.addItem("简→繁", "s2t")
        self._cc_combo.addItem("繁→简", "t2s")
        self._prepare_toolbar_control(self._cc_combo)
        toolbar.addWidget(self._cc_combo)

        # Font dropdown
        font_label = QLabel("字体:")
        font_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self._prepare_toolbar_label(font_label)
        toolbar.addWidget(font_label)

        self._font_combo = QComboBox()
        self._font_combo.addItem("黑体", "apple")
        self._font_combo.addItem("华文中宋", "stzhongsong")
        self._font_combo.setCurrentIndex(1)  # Default to STZhongsong
        self._font_combo.currentIndexChanged.connect(self._on_font_mode_changed)
        self._prepare_toolbar_control(self._font_combo, min_width=118)
        toolbar.addWidget(self._font_combo)

        # Spacing mode dropdown
        spacing_label = QLabel("字间距:")
        spacing_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self._prepare_toolbar_label(spacing_label)
        toolbar.addWidget(spacing_label)

        self._spacing_mode_combo = QComboBox()
        self._spacing_mode_combo.addItem("紧凑", "compact")
        self._spacing_mode_combo.addItem("宽松", "wide")
        self._spacing_mode_combo.setCurrentIndex(1)  # default wide
        self._spacing_mode_combo.currentIndexChanged.connect(self._on_spacing_mode_changed)
        self._prepare_toolbar_control(self._spacing_mode_combo)
        toolbar.addWidget(self._spacing_mode_combo)

        # Line spacing dropdown
        line_label = QLabel("行距:")
        line_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self._prepare_toolbar_label(line_label)
        toolbar.addWidget(line_label)

        self._line_spacing_combo = QComboBox()
        self._line_spacing_combo.addItem("较窄", 0.6)
        self._line_spacing_combo.addItem("标准", 1.0)
        self._line_spacing_combo.addItem("较宽", 2.0)
        self._line_spacing_combo.setCurrentIndex(1)  # Default to 标准
        self._prepare_toolbar_control(self._line_spacing_combo)
        toolbar.addWidget(self._line_spacing_combo)

        self._tone_marks_checkbox = ToolbarCheckBox("音调标线")
        self._tone_marks_checkbox.setFont(self._toolbar_font())
        self._tone_marks_checkbox.setToolTip("在拼音右上角显示音调直线和数字角标")
        self._tone_marks_checkbox.toggled.connect(self.tone_marks_changed.emit)
        toolbar.addWidget(self._tone_marks_checkbox)

        toolbar.addStretch()

        # Favorite button
        self._btn_favorite = QPushButton("⭐ 收藏")
        self._btn_favorite.setObjectName("btn_favorite")
        self._btn_favorite.setToolTip("将当前歌词添加到收藏夹")
        self._btn_favorite.clicked.connect(self.favorite_requested.emit)
        self._prepare_toolbar_button(self._btn_favorite)
        toolbar.addWidget(self._btn_favorite)

        # Export PNG button
        self._btn_export_png = QPushButton("🖼 导出图片")
        self._btn_export_png.setObjectName("btn_export")
        self._btn_export_png.setToolTip("将结果导出为高清PNG图片")
        self._btn_export_png.clicked.connect(self._emit_export_png)
        self._prepare_toolbar_button(self._btn_export_png)
        toolbar.addWidget(self._btn_export_png)

        # Export PDF button
        self._btn_export_pdf = QPushButton("📄 导出PDF")
        self._btn_export_pdf.setObjectName("btn_export")
        self._btn_export_pdf.setToolTip("将结果导出为PDF文件")
        self._btn_export_pdf.clicked.connect(self._emit_export_pdf)
        self._prepare_toolbar_button(self._btn_export_pdf)
        toolbar.addWidget(self._btn_export_pdf)

        # Convert button (primary action)
        self._btn_convert = QPushButton("▶ 开始转换")
        self._btn_convert.setObjectName("btn_convert")
        self._btn_convert.setToolTip("将歌词转换为粤拼注音")
        self._btn_convert.clicked.connect(self._on_convert)
        self._prepare_toolbar_button(self._btn_convert)
        toolbar.addWidget(self._btn_convert)

        layout.addLayout(toolbar)

    def _on_spacing_mode_changed(self):
        mode = self._spacing_mode_combo.currentData()
        self.spacing_mode_changed.emit(mode)

    def _on_font_mode_changed(self):
        mode = self._font_combo.currentData()
        self.font_mode_changed.emit(mode)

    def _emit_export_png(self):
        self.export_png_requested.emit(
            self._font_combo.currentData(),
            self._line_spacing_combo.currentData(),
            self._spacing_mode_combo.currentData(),
            self._tone_marks_checkbox.isChecked()
        )

    def _emit_export_pdf(self):
        self.export_pdf_requested.emit(
            self._font_combo.currentData(),
            self._line_spacing_combo.currentData(),
            self._spacing_mode_combo.currentData(),
            self._tone_marks_checkbox.isChecked()
        )

    def get_spacing_mode(self) -> str:
        return self._spacing_mode_combo.currentData()

    def get_tone_marks_enabled(self) -> bool:
        return self._tone_marks_checkbox.isChecked()

    def get_meta_info(self) -> tuple[str, str]:
        return self._title_input.text().strip(), self._artist_input.text().strip()

    def set_meta_info(self, title: str, artist: str = ""):
        self._title_input.setText(title)
        self._artist_input.setText(artist)

    def _toolbar_font(self) -> QFont:
        font = QFont("Microsoft YaHei UI", 10)
        font.setBold(True)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        return font

    def _prepare_toolbar_label(self, label: QLabel):
        label.setFont(self._toolbar_font())
        label.setMinimumHeight(36)
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def _prepare_toolbar_control(self, widget: QWidget, min_width: int = 96):
        widget.setFont(self._toolbar_font())
        widget.setMinimumHeight(36)
        widget.setMinimumWidth(min_width)
        widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def _prepare_toolbar_button(self, button: QPushButton):
        button.setFont(self._toolbar_font())
        button.setMinimumHeight(36)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def _make_font(self, size: int, bold: bool = False) -> QFont:
        font = QFont()
        font.setPointSize(size)
        if bold:
            font.setBold(True)
        return font

    def _on_text_changed(self):
        text = self._text_edit.toPlainText()
        count = len(text.replace('\n', '').replace(' ', ''))
        self._char_count_label.setText(f"共 {count} 字")

    def _on_convert(self):
        text = self._text_edit.toPlainText().strip()
        if text:
            cc_mode = self._cc_combo.currentData()
            self.convert_requested.emit(text, cc_mode)

    def get_text(self) -> str:
        return self._text_edit.toPlainText()

    def set_text(self, text: str):
        self._text_edit.setPlainText(text)

    def get_cc_mode(self) -> str:
        return self._cc_combo.currentData()

    def set_export_enabled(self, enabled: bool):
        self._btn_export_png.setEnabled(enabled)
        self._btn_export_pdf.setEnabled(enabled)
        self._btn_favorite.setEnabled(enabled)
