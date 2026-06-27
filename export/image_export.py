"""
PNG Image Export: Renders lyrics with Jyutping annotations as a high-quality PNG image.
Uses Pillow for drawing.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from core.converter import LyricsToken
from core.tone_marks import TONE_LINE_LEVELS, split_tone


def _find_cjk_font(size: int, font_mode: str = "stzhongsong") -> ImageFont.FreeTypeFont:
    """
    Find and load a CJK-capable font based on the selected mode.
    """
    if font_mode == "stzhongsong":
        font_candidates = [
            "C:/Windows/Fonts/stzhongs.ttf",    # STZhongsong
            "C:/Windows/Fonts/simsun.ttc",      # SimSun fallback
        ]
    else:
        font_candidates = [
            "C:/Windows/Fonts/msyhbd.ttc",      # Microsoft YaHei Bold
            "C:/Windows/Fonts/msyh.ttc",        # Microsoft YaHei
            "C:/Windows/Fonts/simhei.ttf",      # SimHei
        ]

    for font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue

    # Fallback: use default font
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def export_to_png(
    tokens: list[LyricsToken],
    output_path: str,
    bg_color: str = "#ffffff",
    char_color: str = "#1a1a2e",
    jyutping_color: str = "#004088",
    dpi: int = 300,
    font_mode: str = "stzhongsong",
    line_spacing_multiplier: float = 1.0,
    spacing_mode: str = "wide",
    title: str = "",
    tone_marks_enabled: bool = False,
):
    """
    Export lyrics tokens as a high-quality PNG image with Jyutping annotations.
    """
    # Font sizes (in points, scaled for DPI)
    scale = dpi / 96  # Base DPI is 96
    char_font_size = int(28 * scale)
    jyutping_font_size = int(14 * scale)
    title_font_size = int(40 * scale)

    char_font = _find_cjk_font(char_font_size, font_mode)
    apple_font = _find_cjk_font(char_font_size, "apple")
    try:
        arial_font = ImageFont.truetype("arial.ttf", char_font_size)
    except Exception:
        arial_font = apple_font
    try:
        # Use narrower Latin font for Jyutping
        jyutping_font = ImageFont.truetype("arial.ttf", jyutping_font_size)
    except Exception:
        jyutping_font = _find_cjk_font(jyutping_font_size, font_mode)

    # Layout parameters
    margin = int(60 * scale)
    
    if spacing_mode == "compact":
        cell_width = int(36 * scale)
        jyutping_height = int(14 * scale)
        char_height = int(30 * scale)
        jyutping_font_size = int(12 * scale)
        char_font_size = int(24 * scale)
        jyutping_font = _find_cjk_font(jyutping_font_size, "apple")
        char_font = _find_cjk_font(char_font_size, font_mode)
        try:
            arial_font = ImageFont.truetype("arial.ttf", char_font_size)
        except:
            arial_font = char_font
    else:
        cell_width = int(50 * scale)
        jyutping_height = int(22 * scale)
        char_height = int(36 * scale)
        jyutping_font_size = int(16 * scale)
        char_font_size = int(28 * scale)
        jyutping_font = _find_cjk_font(jyutping_font_size, "apple")
        char_font = _find_cjk_font(char_font_size, font_mode)
        try:
            arial_font = ImageFont.truetype("arial.ttf", char_font_size)
        except:
            arial_font = char_font

    line_spacing = int(20 * scale * line_spacing_multiplier)
    
    # Calculate row heights individually
    def get_row_height(line):
        is_english_only = all(t.is_punctuation or t.char.isascii() for t in line)
        if is_english_only:
            return char_height + line_spacing
        return jyutping_height + char_height + line_spacing

    canvas_width = 2500
    usable_width = canvas_width - margin * 2

    # Group tokens into lines based on pixel width
    lines = []
    current_line = []
    current_line_width = 0

    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)

    for token in tokens:
        if token.is_punctuation and token.char in ('\n', '\r', '\r\n'):
            if current_line:
                lines.append(current_line)
                current_line = []
                current_line_width = 0
            continue
            
        f = arial_font if token.char.isascii() else char_font
        if not token.is_punctuation and not token.char.isascii():
            jp_text = token.current_jyutping or ""
            jp_w = temp_draw.textlength(jp_text, font=jyutping_font)
            char_w = temp_draw.textlength(token.char, font=char_font)
            padding = int(4 * scale) if spacing_mode == "compact" else int(12 * scale)
            w = max(jp_w, char_w) + padding
        else:
            tw = temp_draw.textlength(token.char, font=f)
            if token.char.strip() == "":
                w = int(14 * scale) * max(1, len(token.char))
            else:
                w = tw + int(2 * scale)
                
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

    # Calculate title dimensions
    title_height = 0
    if title:
        title_font = _find_cjk_font(title_font_size, font_mode)
        title_bbox = temp_draw.textbbox((0, 0), title, font=title_font)
        title_height = (title_bbox[3] - title_bbox[1]) + int(40 * scale)

    top_margin = margin + char_height
    canvas_height = int(margin + top_margin + sum(get_row_height(line) for line in lines) + title_height)

    # Create image
    img = Image.new('RGB', (canvas_width, canvas_height), bg_color)
    draw = ImageDraw.Draw(img)
    
    y_cursor = top_margin

    if title:
        draw.text((margin, y_cursor), title, font=title_font, fill=char_color)
        y_cursor += title_height

    # Draw each line
    for line_idx, line in enumerate(lines):
        r_height = get_row_height(line)
        is_english_only = all(t.is_punctuation or t.char.isascii() for t in line)
        x = margin

        for char_idx, token in enumerate(line):
            f = arial_font if token.char.isascii() else char_font
            if not token.is_punctuation and not token.char.isascii():
                jp_text = token.current_jyutping or ""
                jp_w = draw.textlength(jp_text, font=jyutping_font)
                char_w = draw.textlength(token.char, font=char_font)
                padding = int(4 * scale) if spacing_mode == "compact" else int(12 * scale)
                token_width = max(jp_w, char_w) + padding
            else:
                tw = draw.textlength(token.char, font=f)
                if token.char.strip() == "":
                    token_width = int(14 * scale) * max(1, len(token.char))
                else:
                    token_width = tw + int(2 * scale)

            y_offset = 0 if is_english_only else jyutping_height
            draw_color = "#6e7681" if token.char.isascii() else char_color

            if token.is_punctuation:
                # Draw punctuation (no Jyutping)
                _draw_centered_text(
                    draw, token.char, x, y_cursor + y_offset,
                    token_width, char_height, f,
                    fill=draw_color
                )
            else:
                if not is_english_only:
                    # Draw Jyutping text (centered above character)
                    jyutping_text = token.current_jyutping or ""
                    _draw_centered_jyutping(
                        draw, jyutping_text, x, y_cursor,
                        token_width, jyutping_height, jyutping_font,
                        fill=jyutping_color,
                        tone_marks_enabled=tone_marks_enabled
                    )

                # Draw Chinese character (centered below Jyutping)
                _draw_centered_text(
                    draw, token.char, x, y_cursor + y_offset,
                    token_width, char_height, f,
                    fill=draw_color
                )
            x += token_width
            
        y_cursor += r_height

    # Save with high DPI
    img.save(output_path, 'PNG', dpi=(dpi, dpi))


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int, y: int,
    width: int, height: int,
    font: ImageFont.FreeTypeFont,
    fill: str = "#ffffff"
):
    """Draw text centered within a bounding box."""
    if not text:
        return

    text_width = draw.textlength(text, font=font)

    text_x = int(x + (width - text_width) / 2)
    text_y = int(y + (height - font.size) / 2)

    draw.text((text_x, text_y), text, font=font, fill=fill)


def _draw_centered_jyutping(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int, y: int,
    width: int, height: int,
    font: ImageFont.FreeTypeFont,
    fill: str = "#ffffff",
    tone_marks_enabled: bool = False,
):
    """Draw Jyutping text, optionally with a straight tone line and corner digit."""
    parts = split_tone(text) if tone_marks_enabled else None
    if not parts:
        _draw_centered_text(draw, text, x, y, width, height, font, fill)
        return

    base, tone = parts
    line_levels = TONE_LINE_LEVELS.get(tone)
    if not line_levels:
        _draw_centered_text(draw, text, x, y, width, height, font, fill)
        return

    font_size = _font_size(font, height)
    digit_font = _make_variant_font(font, 0.72, font_size)
    digit_font_size = _font_size(digit_font, font_size)

    base_width = draw.textlength(base, font=font)
    digit_width = draw.textlength(tone, font=digit_font)
    mark_width = max(4, int(digit_font_size * 0.58))
    gap = max(1, int(font_size * 0.06))
    group_width = base_width + gap + mark_width + gap + digit_width

    group_x = x + (width - group_width) / 2
    base_y = int(y + (height - font_size) / 2)
    draw.text((group_x, base_y), base, font=font, fill=fill)

    mark_x1 = group_x + base_width + gap
    mark_x2 = mark_x1 + mark_width
    digit_x = mark_x2 + gap
    sup_top = max(y, base_y - int(font_size * 0.18))
    tone_levels = {
        "top": sup_top + digit_font_size * 0.12,
        "middle": sup_top + digit_font_size * 0.45,
        "bottom": sup_top + digit_font_size * 0.78,
    }
    y1 = tone_levels[line_levels[0]]
    y2 = tone_levels[line_levels[1]]

    line_width = max(1, int(font_size * 0.08))
    draw.line((mark_x1, y1, mark_x2, y2), fill=fill, width=line_width)
    draw.text((digit_x, sup_top), tone, font=digit_font, fill=fill)


def _make_variant_font(
    font: ImageFont.FreeTypeFont,
    factor: float,
    fallback_size: int,
) -> ImageFont.FreeTypeFont:
    size = max(1, int(fallback_size * factor))
    try:
        return font.font_variant(size=size)
    except Exception:
        return font


def _font_size(font: ImageFont.FreeTypeFont, fallback: int) -> int:
    return int(getattr(font, "size", fallback))
