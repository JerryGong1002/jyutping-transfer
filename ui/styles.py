"""
QSS Stylesheet and design system constants for the Jyutping Lyrics Converter.
Clean light theme with white background.
"""

# ──────────────────── Color Palette ────────────────────

COLORS = {
    'bg_darkest':       '#f0f2f5',
    'bg_dark':          '#f6f8fa',
    'bg_medium':        '#e5e7eb',
    'bg_card':          '#ffffff',
    'bg_card_hover':    '#f3f4f6',
    'bg_input':         '#ffffff',

    'border':           '#d0d7de',
    'border_focus':     '#0969da',

    'text_primary':     '#24292f',
    'text_secondary':   '#57606a',
    'text_muted':       '#8c959f',

    'accent_blue':      '#004088',
    'accent_teal':      '#1a7f64',
    'accent_coral':     '#cf222e',
    'accent_purple':    '#8250df',
    'accent_green':     '#2da44e',
    'accent_gold':      '#bf8700',

    'gradient_start':   '#0f3460',
    'gradient_end':     '#1a8a7d',

    'btn_primary':      '#2da44e',
    'btn_primary_hover':'#2c974b',
    'btn_danger':       '#cf222e',
    'btn_danger_hover': '#a40e26',

    'polyphonic':       '#cf222e',
    'polyphonic_bg':    'rgba(207, 34, 46, 0.06)',

    'scrollbar_bg':     '#f6f8fa',
    'scrollbar_handle': '#d0d7de',
    'scrollbar_hover':  '#8c959f',
}

# ──────────────────── Spacing Mode Constants ────────────────────

SPACING_MODES = {
    'compact': {
        'jyutping_pt': 8,
        'char_pt': 14,
        'widget_h_spacing': 0,
        'widget_v_spacing': 2,
        'cell_margin_h': 0,
        'cell_margin_v': 0,
        'widget_height': 34,
    },
    'wide': {
        'jyutping_pt': 12,
        'char_pt': 14,
        'widget_h_spacing': 3,
        'widget_v_spacing': 6,
        'cell_margin_h': 4,
        'cell_margin_v': 2,
        'widget_height': 52,
    },
}


# ──────────────────── Font Sizes ────────────────────

FONTS = {
    'family':           "'PingFang SC', 'Microsoft YaHei UI', 'Segoe UI', 'Noto Sans CJK SC', sans-serif",
    'size_xs':          '10px',
    'size_sm':          '12px',
    'size_md':          '13px',
    'size_lg':          '15px',
    'size_xl':          '20px',
    'size_xxl':         '24px',
    'size_jyutping':    '11px',
    'size_hanzi':       '18px',
}


# ──────────────────── Dimensions ────────────────────

DIMS = {
    'sidebar_width':    '240px',
    'border_radius':    '6px',
    'border_radius_sm': '4px',
    'spacing':          '10px',
    'padding':          '12px',
    'padding_sm':       '6px',
}


# ──────────────────── Main Stylesheet ────────────────────

MAIN_STYLESHEET = f"""
/* ═══════════ Global ═══════════ */
QMainWindow {{
    background-color: {COLORS['bg_darkest']};
    color: {COLORS['text_primary']};
    font-family: {FONTS['family']};
    font-size: {FONTS['size_md']};
}}

QWidget {{
    color: {COLORS['text_primary']};
    font-family: {FONTS['family']};
}}

/* ═══════════ Tooltips ═══════════ */
QToolTip {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: {FONTS['size_sm']};
}}

/* ═══════════ Message Box (Dialogs) ═══════════ */
QMessageBox {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
}}
QMessageBox QLabel {{
    color: {COLORS['text_primary']};
}}
QMessageBox QPushButton {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: {DIMS['border_radius_sm']};
    padding: 6px 20px;
    min-width: 70px;
}}
QMessageBox QPushButton:hover {{
    background-color: {COLORS['bg_card_hover']};
    border-color: {COLORS['accent_blue']};
}}

/* ═══════════ Input Dialog ═══════════ */
QInputDialog {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
}}
QInputDialog QLabel {{
    color: {COLORS['text_primary']};
}}
QInputDialog QLineEdit {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: {DIMS['border_radius_sm']};
    padding: 6px;
}}

/* ═══════════ File Dialog ═══════════ */
QFileDialog {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
}}

/* ═══════════ Scrollbars ═══════════ */
QScrollBar:vertical {{
    background: {COLORS['scrollbar_bg']};
    width: 8px;
    margin: 0;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['scrollbar_handle']};
    min-height: 30px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLORS['scrollbar_hover']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background: {COLORS['scrollbar_bg']};
    height: 8px;
    margin: 0;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {COLORS['scrollbar_handle']};
    min-width: 30px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {COLORS['scrollbar_hover']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

/* ═══════════ Scroll Area ═══════════ */
QScrollArea {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: {DIMS['border_radius']};
}}

/* ═══════════ Text Edit ═══════════ */
QTextEdit {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: {DIMS['border_radius']};
    padding: 10px;
    font-size: {FONTS['size_lg']};
    selection-background-color: {COLORS['accent_blue']};
    selection-color: white;
}}
QTextEdit:focus {{
    border-color: {COLORS['border_focus']};
}}

/* ═══════════ Line Edit ═══════════ */
QLineEdit {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: {DIMS['border_radius_sm']};
    padding: 6px 10px;
    font-size: {FONTS['size_md']};
}}
QLineEdit:focus {{
    border-color: {COLORS['border_focus']};
}}

/* ═══════════ Buttons ═══════════ */
QPushButton {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: {DIMS['border_radius_sm']};
    padding: 6px 14px;
    font-size: {FONTS['size_md']};
}}
QPushButton:hover {{
    background-color: {COLORS['bg_card_hover']};
    border-color: {COLORS['accent_blue']};
}}
QPushButton:pressed {{
    background-color: {COLORS['bg_medium']};
}}

/* Primary button */
QPushButton#btn_convert {{
    background-color: {COLORS['btn_primary']};
    border-color: {COLORS['btn_primary']};
    color: {COLORS['text_primary']};
    font-weight: bold;
    font-size: {FONTS['size_md']};
    padding: 6px 20px;
}}
QPushButton#btn_convert:hover {{
    background-color: {COLORS['btn_primary_hover']};
    border-color: {COLORS['btn_primary_hover']};
}}

/* Favorite button */
QPushButton#btn_favorite {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['accent_gold']};
    color: {COLORS['accent_gold']};
    padding: 6px 12px;
}}
QPushButton#btn_favorite:hover {{
    background-color: rgba(191, 135, 0, 0.08);
}}

/* Export button */
QPushButton#btn_export {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['accent_teal']};
    color: {COLORS['accent_teal']};
    padding: 6px 12px;
}}
QPushButton#btn_export:hover {{
    background-color: rgba(26, 127, 100, 0.08);
}}

/* ═══════════ ComboBox ═══════════ */
QComboBox {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: {DIMS['border_radius_sm']};
    padding: 5px 10px;
    font-size: {FONTS['size_md']};
    min-width: 80px;
}}
QComboBox:hover {{
    border-color: {COLORS['accent_blue']};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox::down-arrow {{
    image: none;
    border: none;
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    selection-background-color: {COLORS['accent_blue']};
    selection-color: white;
    padding: 4px;
}}

/* ═══════════ Labels ═══════════ */
QLabel#section_title {{
    color: {COLORS['text_primary']};
    font-size: {FONTS['size_lg']};
    font-weight: bold;
    padding: 2px 0;
}}

QLabel#section_subtitle {{
    color: {COLORS['text_secondary']};
    font-size: {FONTS['size_sm']};
    padding: 2px 0;
}}

/* ═══════════ Menu (for polyphonic popup) ═══════════ */
QMenu {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: {DIMS['border_radius_sm']};
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 20px;
    border-radius: 3px;
    font-size: {FONTS['size_md']};
}}
QMenu::item:selected {{
    background-color: {COLORS['accent_blue']};
    color: white;
}}
QMenu::separator {{
    height: 1px;
    background: {COLORS['border']};
    margin: 3px 6px;
}}

/* ═══════════ Splitter ═══════════ */
QSplitter::handle {{
    background-color: {COLORS['border']};
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}

/* ═══════════ List Widget (sidebar) ═══════════ */
QListWidget {{
    background-color: {COLORS['bg_dark']};
    border: none;
    outline: none;
    font-size: {FONTS['size_md']};
}}
QListWidget::item {{
    padding: 8px 12px;
    border-radius: {DIMS['border_radius_sm']};
    margin: 1px 4px;
    color: {COLORS['text_primary']};
}}
QListWidget::item:hover {{
    background-color: {COLORS['bg_card_hover']};
}}
QListWidget::item:selected {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['accent_blue']};
    border-left: 3px solid {COLORS['accent_blue']};
}}

/* ═══════════ Status Bar ═══════════ */
QStatusBar {{
    background-color: {COLORS['bg_darkest']};
    color: {COLORS['text_muted']};
    border-top: 1px solid {COLORS['border']};
    font-size: {FONTS['size_sm']};
    padding: 2px 8px;
}}
"""


# ──────────────────── Sidebar Stylesheet ────────────────────

SIDEBAR_STYLESHEET = f"""
QWidget#sidebar {{
    background-color: {COLORS['bg_dark']};
    border-right: 1px solid {COLORS['border']};
}}

QPushButton#nav_button {{
    background-color: transparent;
    border: none;
    border-radius: {DIMS['border_radius_sm']};
    color: {COLORS['text_secondary']};
    text-align: left;
    padding: 8px 14px;
    font-size: {FONTS['size_md']};
}}
QPushButton#nav_button:hover {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
}}
QPushButton#nav_button:checked {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['accent_blue']};
    border-left: 3px solid {COLORS['accent_blue']};
}}

QLabel#sidebar_header {{
    color: {COLORS['text_muted']};
    font-size: {FONTS['size_xs']};
    font-weight: bold;
    letter-spacing: 1px;
    padding: 10px 14px 4px 14px;
}}

QLabel#app_title {{
    color: {COLORS['text_primary']};
    font-size: {FONTS['size_xl']};
    font-weight: bold;
    padding: 16px 14px 2px 14px;
}}

QLabel#app_subtitle {{
    color: {COLORS['accent_teal']};
    font-size: {FONTS['size_sm']};
    padding: 0px 14px 12px 14px;
}}
"""


# ──────────────────── Word Widget Stylesheet ────────────────────

WORD_WIDGET_NORMAL = f"""
QWidget#word_widget {{
    background-color: transparent;
    border: none;
}}
QWidget#word_widget:hover {{
    background-color: rgba(9, 105, 218, 0.05);
}}
"""

WORD_WIDGET_POLYPHONIC = f"""
QWidget#word_widget {{
    background-color: {COLORS['polyphonic_bg']};
    border: 1px solid rgba(207, 34, 46, 0.12);
    border-radius: 3px;
}}
QWidget#word_widget:hover {{
    background-color: rgba(207, 34, 46, 0.1);
    border-color: rgba(207, 34, 46, 0.25);
}}
"""
