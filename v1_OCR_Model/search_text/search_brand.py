import re
from difflib import get_close_matches

from search_text.indian_brand_lexicon import INDIAN_BRAND_LEXICON


BRAND_STOPWORDS = {
    "tablet",
    "tablets",
    "capsule",
    "capsules",
    "dosage",
    "warning",
    "children",
    "contains",
    "regd",
    "trade",
    "mark",
    "physician",
    "store",
    "moisture",
    "india",
    "made",
    "reach",
    "keep",
    "each",
    "directed",
}


def _normalize_ocr_text(text):
    replacements = {
        "Â©": "©",
        "Â®": "®",
        "â„¢": "™",
        "â€™": "’",
        "â€˜": "'",
        "‘": "'",
        "`": "'",
    }
    normalized = text
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _clean_token(token):
    cleaned = re.sub(r"[^A-Za-z0-9&\-]", "", token or "")
    return cleaned


def _is_plausible_brand(token):
    if not token:
        return False
    if len(token) < 4:
        return False
    lowered = token.lower()
    if lowered in BRAND_STOPWORDS:
        return False
    if lowered.isdigit():
        return False
    return True


def _match_symbol_adjacent_brand(text):
    """
    Strategy A:
    Match token directly before trademark-like symbol.
    Includes apostrophe as OCR fallback for missed ®.
    """
    pattern = r"\b([A-Za-z][A-Za-z0-9&\-]{2,})\s*[©®™'’]"
    for match in re.finditer(pattern, text):
        candidate = _clean_token(match.group(1))
        if _is_plausible_brand(candidate):
            return candidate
    return None


def _match_trademark_context_brand(text):
    """
    Strategy B:
    If OCR turns ® into text context, look for candidate immediately before
    nearby 'Regd'/'Trade Mark' marker.
    """
    pattern = r"\b([A-Za-z][A-Za-z0-9&\-]{2,})\b(?=.{0,24}\b(?:Regd|Trade\s*Mark)\b)"
    for match in re.finditer(pattern, text, flags=re.IGNORECASE):
        candidate = _clean_token(match.group(1))
        if _is_plausible_brand(candidate):
            return candidate
    return None


def _match_strength_line_brand(text):
    """
    Strategy C:
    Match brand-like token followed by strength number (e.g., 'Pacimol 500').
    """
    pattern = r"\b([A-Za-z][A-Za-z0-9&\-]{3,})['’]?\s*[-]?\s*(\d{2,4})\b"
    for match in re.finditer(pattern, text):
        candidate = _clean_token(match.group(1))
        if _is_plausible_brand(candidate):
            return candidate
    return None


def _match_lexicon_brand(text):
    """
    Strategy D:
    Fallback to Indian pharma brand lexicon with exact/fuzzy matching.
    """
    lexicon_map = {name.lower().replace(" ", ""): name for name in INDIAN_BRAND_LEXICON}
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9'&\-]{2,}", text)

    for token in tokens:
        candidate = _clean_token(token).lower().replace(" ", "")
        if not _is_plausible_brand(candidate):
            continue
        if candidate in lexicon_map:
            return lexicon_map[candidate]

    normalized_keys = list(lexicon_map.keys())
    for token in tokens:
        candidate = _clean_token(token).lower().replace(" ", "")
        if not _is_plausible_brand(candidate):
            continue
        matches = get_close_matches(candidate, normalized_keys, n=1, cutoff=0.84)
        if matches:
            return lexicon_map[matches[0]]

    return None

def search_brand_name(text):
    """
    Multi-strategy brand extraction for noisy OCR output.

    Returns the most likely brand name.
    Returns None if nothing is found.
    """
    normalized_text = _normalize_ocr_text(text)
    strategy_order = (
        _match_symbol_adjacent_brand,
        _match_trademark_context_brand,
        _match_lexicon_brand,
        _match_strength_line_brand,
    )

    for strategy in strategy_order:
        brand_name = strategy(normalized_text)
        if brand_name:
            return brand_name
    return None
