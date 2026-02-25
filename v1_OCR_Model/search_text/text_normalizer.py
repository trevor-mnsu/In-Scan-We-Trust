import re


UNIT_CANONICAL = {
    "mg": "mg",
    "g": "g",
    "mcg": "mcg",
    "kg": "kg",
    "ml": "mL",
    "iu": "IU",
}


def _normalize_mojibake(text):
    replacements = {
        "Â©": "\u00A9",
        "Â®": "\u00AE",
        "â„¢": "\u2122",
        "Î¼g": "mcg",
        "μg": "mcg",
        "ug": "mcg",
        "Ã‚Â©": "\u00A9",
        "Ã‚Â®": "\u00AE",
        "Ã¢â€žÂ¢": "\u2122",
        "ÃŽÂ¼g": "mcg",
        "ÃŽÂ¼": "mcg",
        "Ã‚ ": " ",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def _normalize_unit_tokens(text):
    text = re.sub(r"(?i)\bm\s*g\b", "mg", text)
    text = re.sub(r"(?i)\bm\s*c\s*g\b", "mcg", text)
    text = re.sub(r"(?i)\bm\s*l\b", "mL", text)
    text = re.sub(r"(?i)\bi\s*u\b", "IU", text)

    def _fix_number_unit(match):
        number = match.group(1)
        unit = UNIT_CANONICAL[match.group(2).lower()]
        return f"{number} {unit}"

    text = re.sub(
        r"(?i)\b(\d+(?:\.\d+)?)\s*(mg|g|mcg|kg|ml|iu)\b",
        _fix_number_unit,
        text,
    )

    return text


def normalize_ocr_text(raw_text):
    raw_text = raw_text or ""
    text = _normalize_mojibake(raw_text)
    text = _normalize_unit_tokens(text)

    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    normalized_lines = [line for line in lines if line]
    normalized_text = "\n".join(normalized_lines)

    return {
        "raw_text": raw_text,
        "normalized_text": normalized_text,
        "normalized_lines": normalized_lines,
    }
