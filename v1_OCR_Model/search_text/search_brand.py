import re


BRAND_CONTEXT_PATTERN = re.compile(
    r"(?i)\b(brand|trademark|tm|by)\b"
)


def _clean_token(token):
    return token.strip(" -:;,.()[]{}")


def search_brand_name(text, normalized_lines=None):
    """
    Finds a brand name in OCR text.
    Priority:
    1) token near trademark symbols
    2) fallback from explicit brand context lines
    """
    if not text:
        return None

    symbol_pattern = re.compile(
        r"\b([A-Za-z][A-Za-z0-9&\-]{1,30})\s*(?:[\u00A9\u00AE\u2122]|[Â][\u00A9\u00AE]|â„¢)"
    )
    symbol_match = symbol_pattern.search(text)
    if symbol_match:
        return _clean_token(symbol_match.group(1))

    lines = normalized_lines if normalized_lines is not None else text.splitlines()
    lines = [line.strip() for line in lines if line and line.strip()]

    for line in lines[:8]:
        if not BRAND_CONTEXT_PATTERN.search(line):
            continue

        labeled = re.search(
            r"(?i)\b(?:brand|trademark|by)\s*[:\-]?\s*([A-Za-z][A-Za-z0-9&\-\s]{1,40})",
            line,
        )
        if not labeled:
            continue

        candidate = _clean_token(labeled.group(1).split()[0])
        if len(candidate) >= 3:
            return candidate

    return None
