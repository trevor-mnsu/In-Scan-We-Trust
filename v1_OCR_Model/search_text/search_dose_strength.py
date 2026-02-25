import re


UNIT_PRIORITY = {
    "mg": 4,
    "g": 4,
    "mcg": 4,
    "mL": 3,
    "IU": 2,
    "kg": 1,
}


def _canonical_unit(unit):
    lower = unit.lower()
    if lower == "ml":
        return "mL"
    if lower == "iu":
        return "IU"
    return lower


def _line_quality_score(line):
    letters = sum(char.isalpha() for char in line)
    chars = max(1, len(line))
    alpha_ratio = letters / chars

    score = 0
    if 0.15 <= alpha_ratio <= 0.95:
        score += 1
    if len(line) >= 5:
        score += 1
    return score


def search_dosage_amount(text, normalized_lines=None):
    """
    Finds the best dosage candidate and returns normalized output:
    "<number> <unit>", e.g. "500 mg".
    """
    if not text:
        return None

    lines = normalized_lines if normalized_lines is not None else text.splitlines()
    if not lines:
        return None

    pattern = re.compile(
        r"(?i)(?<![A-Za-z0-9])(\d+(?:\.\d+)?)\s*(mg|g|mcg|kg|ml|mL|iu)(?![A-Za-z0-9])"
    )

    best = None
    best_score = -1.0

    for line_idx, line in enumerate(lines):
        for match in pattern.finditer(line):
            number = match.group(1)
            unit = _canonical_unit(match.group(2))

            score = float(UNIT_PRIORITY.get(unit, 0))
            score += _line_quality_score(line)

            exact_span = match.group(0)
            if re.fullmatch(r"\d+(?:\.\d+)?\s+(mg|g|mcg|kg|mL|IU)", exact_span):
                score += 2

            score -= line_idx * 0.01

            if score > best_score:
                best_score = score
                best = f"{number} {unit}"

    return best


def search_dose_strength(text, normalized_lines=None):
    # Backward-compatible wrapper.
    return search_dosage_amount(text, normalized_lines=normalized_lines)
