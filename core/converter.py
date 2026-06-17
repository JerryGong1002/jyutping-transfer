"""
NLP Engine: Converts Chinese lyrics text into structured LyricsToken list
with Jyutping romanization and polyphonic character detection.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class LyricsToken:
    """Represents a single character in the lyrics with its Jyutping annotation."""
    index: int                              # Absolute position in lyrics
    char: str                               # The character itself
    current_jyutping: Optional[str] = None  # Currently selected Jyutping
    is_polyphonic: bool = False             # True if multiple candidates exist
    candidates: list[str] = field(default_factory=list)  # All candidate Jyutpings
    is_punctuation: bool = False            # True for spaces, punctuation, newlines

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'LyricsToken':
        """Deserialize from dictionary."""
        return cls(**data)


def convert_lyrics(text: str, cc_mode: str = 'none') -> list[LyricsToken]:
    """
    Convert lyrics text to a list of LyricsToken objects.

    Args:
        text: Raw lyrics text (can be simplified or traditional Chinese)
        cc_mode: Character conversion mode:
                 'none' - no conversion
                 's2t'  - simplified to traditional
                 't2s'  - traditional to simplified

    Returns:
        List of LyricsToken objects with Jyutping annotations
    """
    import ToJyutping

    # Step 1: Apply OpenCC conversion if requested
    if cc_mode != 'none':
        from opencc import OpenCC
        converter = OpenCC(cc_mode)
        text = converter.convert(text)

    # Step 2: Get best-guess Jyutping for each character
    jyutping_list = ToJyutping.get_jyutping_list(text)

    # Step 3: Get all candidate Jyutpings for each character
    candidates_list = ToJyutping.get_jyutping_candidates(text)

    # Step 4: Build the Token list
    tokens: list[LyricsToken] = []
    
    current_word = []
    def flush_word(offset):
        if current_word:
            word_str = "".join(current_word)
            tokens.append(LyricsToken(
                index=len(tokens),
                char=word_str,
                current_jyutping=None,
                is_polyphonic=False,
                candidates=[],
                is_punctuation=True,
            ))
            current_word.clear()

    for (char, best_jyutping), (_, candidates) in zip(jyutping_list, candidates_list):
        is_punct = best_jyutping is None
        
        # Check if it's an ASCII character (letter, number, or basic punctuation)
        # We don't group spaces or newlines to maintain word boundaries.
        import re
        is_ascii_word_char = is_punct and bool(re.match(r"^[a-zA-Z0-9'\-]+$", char))
        
        if is_ascii_word_char:
            current_word.append(char)
        else:
            flush_word(0)
            
            if is_punct:
                token = LyricsToken(
                    index=len(tokens),
                    char=char,
                    current_jyutping=None,
                    is_polyphonic=False,
                    candidates=[],
                    is_punctuation=True,
                )
            else:
                is_poly = len(candidates) > 1
                token = LyricsToken(
                    index=len(tokens),
                    char=char,
                    current_jyutping=best_jyutping,
                    is_polyphonic=is_poly,
                    candidates=list(candidates),
                    is_punctuation=False,
                )
            tokens.append(token)
            
    flush_word(0)

    return tokens


def tokens_to_json(tokens: list[LyricsToken]) -> str:
    """Serialize a list of LyricsToken to JSON string."""
    return json.dumps([t.to_dict() for t in tokens], ensure_ascii=False)


def tokens_from_json(json_str: str) -> list[LyricsToken]:
    """Deserialize a list of LyricsToken from JSON string."""
    data = json.loads(json_str)
    return [LyricsToken.from_dict(d) for d in data]


def apply_cc_only(text: str, cc_mode: str) -> str:
    """
    Apply OpenCC conversion without Jyutping processing.
    Useful for previewing the conversion result before annotating.
    """
    if cc_mode == 'none':
        return text
    from opencc import OpenCC
    converter = OpenCC(cc_mode)
    return converter.convert(text)
