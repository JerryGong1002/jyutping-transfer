"""Helpers for rendering Jyutping tone-line annotations."""

from __future__ import annotations

import re


_TONE_RE = re.compile(r"^(.*?)([1-6])$")

TONE_LINE_LEVELS = {
    "1": ("top", "top"),
    "2": ("middle", "top"),
    "3": ("middle", "middle"),
    "4": ("middle", "bottom"),
    "5": ("bottom", "middle"),
    "6": ("bottom", "bottom"),
}


def split_tone(text: str) -> tuple[str, str] | None:
    """Split a Jyutping syllable into base spelling and final tone digit."""
    match = _TONE_RE.match(text or "")
    if not match:
        return None

    base, tone = match.groups()
    if not base:
        return None

    return base, tone
