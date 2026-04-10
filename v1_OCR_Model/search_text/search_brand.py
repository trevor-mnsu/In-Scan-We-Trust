import re
from difflib import get_close_matches

from search_text.indian_brand_lexicon import INDIAN_BRAND_LEXICON


# -------------------------------
# Helpers
# -------------------------------

def _normalize_text(text):
    replacements = {
        "Â©": "©",
        "Â®": "®",
        "â„¢": "™",
        "â€™": "’",
        "â€˜": "'",
        "‘": "'",
        "`": "'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _clean_token(token):
    return re.sub(r"[^A-Za-z0-9\-]", "", token or "")


def _is_valid_token(token):
    if not token:
        return False
    if len(token) < 4:
        return False
    if token.isdigit():
        return False

    # Reject codes like N757
    if re.match(r"^[A-Za-z]\d+$", token):
        return False

    return True


# -------------------------------
# STEP 1: Lexicon Match (Highest Confidence)
# -------------------------------

def _match_lexicon(text):
    lexicon_map = {
        name.lower().replace(" ", ""): name
        for name in INDIAN_BRAND_LEXICON
    }

    tokens = re.findall(r"[A-Za-z][A-Za-z0-9'\-]{2,}", text)

    for token in tokens:
        cleaned = _clean_token(token).lower().replace(" ", "")
        if cleaned in lexicon_map:
            return lexicon_map[cleaned]

    # Fuzzy fallback
    keys = list(lexicon_map.keys())
    for token in tokens:
        cleaned = _clean_token(token).lower().replace(" ", "")
        if not _is_valid_token(cleaned):
            continue

        match = get_close_matches(cleaned, keys, n=1, cutoff=0.85)
        if match:
            return lexicon_map[match[0]]

    return None


# -------------------------------
# STEP 2: First letter capital + Strength Pattern
# e.g. "BRUFEN-600", "Pacimol 500"
# -------------------------------

import re

def _match_strength_pattern(text):
    # ✅ Only allow realistic medicine strengths
    VALID_STRENGTHS = {
        "10", "25", "100", "125", "200", "250", "300",
        "400", "500", "550", "600", "650",
        "750", "800", "1000"
    }

    pattern = r"\b([A-Z][a-z]{2,}|[A-Z]{3,})(?:[\s\-])(\d{2,4})\b"

    for match in re.finditer(pattern, text):
        brand = _clean_token(match.group(1))
        strength = match.group(2)

        # ✅ Strict validation
        if not brand or not brand[0].isupper():
            continue

        if not _is_valid_token(brand):
            continue

        if strength not in VALID_STRENGTHS:
            continue

        return brand  # first valid match only

    return None

# -------------------------------
# MAIN FUNCTION
# -------------------------------

def search_brand_name(text):
    """
    Priority:
    1. Lexicon match (exact / fuzzy)
    2. Strength pattern (e.g., Pacimol 500, Brufen-600)
    3. Capitalized heuristic
    """

    text = _normalize_text(text)

    # Step 1: Lexicon
    brand = _match_lexicon(text)
    if brand:
        return brand

    # Step 2: Capital + Strength pattern
    brand = _match_strength_pattern(text)
    if brand:
        return brand

    return None