"""
PDF Export: Renders lyrics with Jyutping annotations as a formatted PDF document.
Uses reportlab for PDF generation.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

from core.converter import LyricsToken
from core.tone_marks import TONE_LINE_LEVELS, split_tone


def _register_cjk_font(font_mode: str = "apple") -> str:
    """
    Register a CJK font with reportlab and return the font name.
    Tries several common Windows fonts.
    """
    if font_mode == "stzhongsong":
        font_candidates = [
            ("STZhongsong", "C:/Windows/Fonts/stzhongs.ttf"),
            ("SimSun", "C:/Windows/Fonts/simsun.ttc"),
        ]
    else:
        font_candidates = [
            ("MicrosoftYaHeiBold", "C:/Windows/Fonts/msyhbd.ttc"),
            ("MicrosoftYaHei", "C:/Windows/Fonts/msyh.ttc"),
            ("SimHei", "C:/Windows/Fonts/simhei.ttf"),
        ]

    for font_name, font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
            except Exception:
                continue

    # If no CJK font found, use Helvetica as fallback (won't render CJK well)
    return "Helvetica"


def export_to_pdf(
    tokens: list[LyricsToken],
    output_path: str,
    title: str = "粵拼注音歌詞",
    font_mode: str = "apple",
    line_spacing_multiplier: float = 1.0,
    spacing_mode: str = "wide",
    tone_marks_enabled: bool = False,
):
    """
    Export lyrics tokens as a PDF document with Jyutping annotations.
    """
    # Register CJK font
    font_name = _register_cjk_font(font_mode)
    jyutping_font_name = "Helvetica-Bold"  # use bold Latin font for Jyutping

    # Page setup
    page_width, page_height = A4
    margin_left = 25 * mm
    margin_right = 25 * mm
    margin_top = 30 * mm
    margin_bottom = 25 * mm

    # Font sizes and dimensions based on spacing mode
    if spacing_mode == "compact":
        char_font_size = 14
        jyutping_font_size = 8
        jyutping_height = 6
        char_height = 12
        cell_width = 18
    else:
        char_font_size = 16
        jyutping_font_size = 10
        jyutping_height = 8
        char_height = 14
        cell_width = 24
        
    title_font_size = 22

    line_spacing = int(12 * line_spacing_multiplier)
    
    def get_row_height(line):
        is_english_only = all(t.is_punctuation or t.char.isascii() for t in line)
        if is_english_only:
            return char_height + line_spacing
        return jyutping_height + char_height + line_spacing

    # Colors
    bg_color = HexColor("#ffffff")
    char_color = HexColor("#1a1a2e")
    jyutping_color = HexColor("#004088")
    title_color = HexColor("#1a1a2e")
    muted_color = HexColor("#6e7681")

    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle(title)

    usable_width = page_width - margin_left - margin_right
    y_cursor = page_height - margin_top

    # Split tokens into lines based on pixel width
    lines = []
    current_line = []
    current_line_width = 0

    for token in tokens:
        if token.is_punctuation and token.char in ('\n', '\r', '\r\n'):
            if current_line:
                lines.append(current_line)
                current_line = []
                current_line_width = 0
            continue
            
        f = "Helvetica" if token.char.isascii() else font_name
        if not token.is_punctuation and not token.char.isascii():
            jp_text = token.current_jyutping or ""
            jp_w = c.stringWidth(jp_text, jyutping_font_name, jyutping_font_size)
            char_w = c.stringWidth(token.char, font_name, char_font_size)
            padding = 2 if spacing_mode == "compact" else 6
            w = max(jp_w, char_w) + padding
        else:
            tw = c.stringWidth(token.char, f, char_font_size)
            if token.char.strip() == "":
                w = 10 * max(1, len(token.char))
            else:
                w = tw + 1
                
        if current_line_width + w > usable_width and current_line:
            lines.append(current_line)
            current_line = [token]
            current_line_width = w
        else:
            current_line.append(token)
            current_line_width += w
            
    if current_line:
        lines.append(current_line)
    if not lines:
        lines = [[]]

    # Draw Title
    c.setFont(font_name, title_font_size)
    c.setFillColor(title_color)
    c.drawString(margin_left, y_cursor, title)
    y_cursor -= 12

    # Subtitle
    c.setFont(font_name, 9)
    c.setFillColor(muted_color)
    c.drawString(margin_left, y_cursor, "Jyutping Lyrics - 粵語拼音自動標註")
    y_cursor -= 8

    # Separator line
    c.setStrokeColor(HexColor("#e0e0e0"))
    c.setLineWidth(0.5)
    c.line(margin_left, y_cursor, page_width - margin_right, y_cursor)
    y_cursor -= 20

    # Draw Lyrics Lines
    for line in lines:
        r_height = get_row_height(line)
        is_english_only = all(t.is_punctuation or t.char.isascii() for t in line)
        # Check if we need a new page
        if y_cursor - r_height < margin_bottom:
            c.showPage()
            y_cursor = page_height - margin_top

        x = margin_left

        for token in line:
            f = "Helvetica" if token.char.isascii() else font_name
            if not token.is_punctuation and not token.char.isascii():
                jp_text = token.current_jyutping or ""
                jp_w = c.stringWidth(jp_text, jyutping_font_name, jyutping_font_size)
                char_w = c.stringWidth(token.char, font_name, char_font_size)
                padding = 2 if spacing_mode == "compact" else 6
                token_width = max(jp_w, char_w) + padding
            else:
                tw = c.stringWidth(token.char, f, char_font_size)
                if token.char.strip() == "":
                    token_width = 10 * max(1, len(token.char))
                else:
                    token_width = tw + 1

            y_offset = 0 if is_english_only else jyutping_height
            draw_color = muted_color if token.char.isascii() else char_color

            if token.is_punctuation:
                # Draw punctuation character only
                c.setFont(f, char_font_size)
                c.setFillColor(draw_color)
                _draw_centered_pdf(
                    c, token.char, x, y_cursor - y_offset,
                    token_width, char_height, f, char_font_size
                )
            else:
                if not is_english_only:
                    # Draw Jyutping above
                    jyutping_text = token.current_jyutping or ""
                    c.setFillColor(jyutping_color)
                    _draw_centered_jyutping_pdf(
                        c, jyutping_text, x, y_cursor,
                        token_width, jyutping_height, jyutping_font_name, jyutping_font_size,
                        fill_color=jyutping_color,
                        tone_marks_enabled=tone_marks_enabled
                    )
                # Draw character
                c.setFont(f, char_font_size)
                c.setFillColor(draw_color)
                _draw_centered_pdf(
                    c, token.char, x, y_cursor - y_offset,
                    token_width, char_height, f, char_font_size
                )
            
            x += token_width
            
        y_cursor -= r_height

    # Footer
    c.setFont(font_name, 7)
    c.setFillColor(muted_color)
    c.drawString(
        margin_left,
        margin_bottom - 10,
        "Generated by 粵拼注音 - Jyutping Lyrics Converter"
    )

    c.save()


def _draw_centered_pdf(
    c: canvas.Canvas,
    text: str,
    x: float, y: float,
    width: float, height: float,
    font_name: str, font_size: float
):
    """Draw text centered within a bounding box on the PDF canvas."""
    if not text:
        return

    c.setFont(font_name, font_size)
    text_width = c.stringWidth(text, font_name, font_size)
    text_x = x + (width - text_width) / 2
    text_y = y - height + (height - font_size) / 2 + 2

    c.drawString(text_x, text_y, text)


def _draw_centered_jyutping_pdf(
    c: canvas.Canvas,
    text: str,
    x: float, y: float,
    width: float, height: float,
    font_name: str, font_size: float,
    fill_color=None,
    tone_marks_enabled: bool = False,
):
    """Draw Jyutping text, optionally with a straight tone line and corner digit."""
    parts = split_tone(text) if tone_marks_enabled else None
    if not parts:
        _draw_centered_pdf(c, text, x, y, width, height, font_name, font_size)
        return

    base, tone = parts
    line_levels = TONE_LINE_LEVELS.get(tone)
    if not line_levels:
        _draw_centered_pdf(c, text, x, y, width, height, font_name, font_size)
        return

    digit_font_size = max(1, font_size * 0.72)
    base_width = c.stringWidth(base, font_name, font_size)
    digit_width = c.stringWidth(tone, font_name, digit_font_size)
    mark_width = max(2, digit_font_size * 0.58)
    gap = max(0.5, font_size * 0.06)
    group_width = base_width + gap + mark_width + gap + digit_width

    group_x = x + (width - group_width) / 2
    base_y = y - height + (height - font_size) / 2 + 2

    if fill_color is not None:
        c.setFillColor(fill_color)
        c.setStrokeColor(fill_color)

    c.setFont(font_name, font_size)
    c.drawString(group_x, base_y, base)

    mark_x1 = group_x + base_width + gap
    mark_x2 = mark_x1 + mark_width
    digit_x = mark_x2 + gap

    tone_levels = {
        "top": base_y + font_size * 0.78,
        "middle": base_y + font_size * 0.52,
        "bottom": base_y + font_size * 0.26,
    }
    y1 = tone_levels[line_levels[0]]
    y2 = tone_levels[line_levels[1]]

    c.setLineWidth(max(0.4, font_size * 0.08))
    c.line(mark_x1, y1, mark_x2, y2)

    c.setFont(font_name, digit_font_size)
    c.drawString(digit_x, base_y + font_size * 0.36, tone)
