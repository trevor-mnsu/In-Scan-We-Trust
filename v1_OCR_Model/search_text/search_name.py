import re


METADATA_PATTERN = re.compile(
    r"(?i)\b(lot|batch|exp|expiry|mfg|manufact|date|use by|mrp|price|lic|license)\b"
)
COMPOSITION_PATTERN = re.compile(
    r"(?i)\b(each\s+tablet\s+contains|composition|contains|ingredients?)\b"
)
DOSAGE_ONLY_PATTERN = re.compile(
    r"(?i)^\d+(?:\.\d+)?\s*(mg|g|mcg|kg|ml|mL|IU)$"
)


def _tokenize_alpha_num(line):
    return re.findall(r"[A-Za-z0-9\-]+", line)


def _is_probable_code(line):
    compact = re.sub(r"[^A-Za-z0-9]", "", line)
    return bool(re.fullmatch(r"[A-Z0-9]{1,4}", compact))


def _score_candidate(line):
    if DOSAGE_ONLY_PATTERN.match(line):
        return None
    if METADATA_PATTERN.search(line):
        return None
    if COMPOSITION_PATTERN.search(line):
        return None
    if _is_probable_code(line):
        return None
    if not re.search(r"[A-Z]", line):
        return None

    tokens = _tokenize_alpha_num(line)
    if not tokens:
        return None

    alpha_count = sum(char.isalpha() for char in line)
    char_count = max(1, len(line))
    alpha_ratio = alpha_count / char_count
    digit_count = sum(char.isdigit() for char in line)
    digit_ratio = digit_count / char_count

    score = 0.0

    token_count = len(tokens)
    if 1 <= token_count <= 5:
        score += 3
    elif token_count <= 8:
        score += 1
    else:
        score -= 2

    if alpha_ratio >= 0.6:
        score += 2
    elif alpha_ratio >= 0.4:
        score += 1
    else:
        score -= 2

    if digit_ratio > 0.35:
        score -= 2

    if any(re.search(r"[A-Za-z]", token) for token in tokens):
        score += 1
    else:
        score -= 2

    if any(token and token[0].isupper() for token in tokens):
        score += 1
    else:
        score -= 2

    if re.search(r"[^\w\s\-\(\)]", line):
        score -= 1

    if len(line) < 4:
        score -= 2

    if re.search(r"(?i)\b(tablet|capsule|film|coated)\b", line):
        score += 1

    return score


def search_medicine_name(text, normalized_lines=None):
    """
    Picks the best medication-name candidate from top OCR lines.
    Returns None when confidence is low.
    """
    if not text:
        return None

    lines = normalized_lines if normalized_lines is not None else text.splitlines()
    lines = [line.strip() for line in lines if line and line.strip()]
    if not lines:
        return None

    best_line = None
    best_score = -999.0

    for idx, line in enumerate(lines[:8]):
        score = _score_candidate(line)
        if score is None:
            continue

        score -= idx * 0.05

        if score > best_score:
            best_score = score
            best_line = line

    if best_line is None or best_score < 3.5:
        return None

    return re.sub(r"\s+", " ", best_line).strip()


def search_medicine_name_first_line(text, normalized_lines=None):
    # Backward-compatible wrapper.
    return search_medicine_name(text, normalized_lines=normalized_lines)
