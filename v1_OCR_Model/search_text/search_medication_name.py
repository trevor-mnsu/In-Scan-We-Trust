import csv
import re
from dataclasses import dataclass
from difflib import SequenceMatcher, get_close_matches
from functools import lru_cache
from pathlib import Path


FUZZY_MATCH_THRESHOLD = 0.93
MAX_NGRAM_WORDS = 6

# Minimum word length to avoid false positives on short tokens.
MIN_WORD_LEN = 4


# Common pharmaceutical prefixes and suffixes used in generic drug naming.
MED_PREFIXES = [
    "ace", "acet", "amox", "ampi", "ator", "azi", "benzo", "bupro",
    "carba", "cepha", "chlor", "cip", "clari", "clinda", "clopi",
    "cyclo", "dexa", "diaz", "diclo", "digox", "dilt", "doxy",
    "enala", "erythro", "esomep", "estradi", "fluox", "fluco",
    "furo", "gabap", "glip", "gluco", "hydro", "ibup", "insulin",
    "irbesar", "isosorbide", "keto", "levo", "lisi", "lora",
    "losart", "meto", "metroni", "mido", "mino", "morph",
    "napro", "nifed", "nitro", "omep", "oxyco", "para",
    "panto", "pred", "propr", "quetiap", "rami", "rifamp",
    "risper", "rosuvast", "sertra", "simvast", "sumat",
    "tamox", "temazep", "tramad", "valsar", "vancom",
    "venlafax", "warfar", "zolp",
]

MED_SUFFIXES = [
    "afil", "alol", "amine", "amol", "anol", "anserin", "artan",
    "ase", "asin", "asone", "astine", "azosin", "barb", "bital",
    "caine", "cillin", "clasone", "corti", "cycline", "dipine",
    "done", "dronate", "fenac", "floxacin", "gliptin", "ide",
    "ifene", "illin", "imab", "ine", "ipine", "irine", "irox",
    "isone", "itib", "ium", "izine", "lamide", "lam", "lapril",
    "limus", "lone", "lopram", "losin", "lukast", "mab", "mycin",
    "nacin", "napril", "nib", "nicol", "nitrate", "nolol", "olol",
    "omide", "omycin", "opril", "osartan", "oxacin", "oxetine",
    "oxin", "pam", "parin", "prazole", "pril", "profen",
    "razine", "restat", "ridol", "rine", "sartan", "semide",
    "setron", "statin", "sulide", "tadine", "tazole", "thrin",
    "tidine", "tilidine", "tinib", "triptan", "tyline", "uride",
    "vastatin", "vir", "vudine", "xaban", "xine", "xole", "zide",
    "zine", "zosin", "zumab",
]


@dataclass(frozen=True)
class MedicationMatch:
    medication_name: str
    confidence: float
    source: str


@dataclass(frozen=True)
class OCRMedicationCandidate:
    method: str
    ocr_confidence: float
    text: str


@dataclass(frozen=True)
class _MedicationLexicon:
    exact_index: dict[str, str]
    normalized_keys: list[str]
    max_words: int


def _normalize_for_match(value: str) -> str:
    normalized = (value or "").lower()
    normalized = normalized.replace("&", " and ")
    normalized = normalized.replace("/", " ")
    normalized = normalized.replace("-", " ")
    normalized = normalized.replace("+", " + ")
    normalized = re.sub(r"[()]", " ", normalized)
    normalized = re.sub(r"[^a-z0-9+\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _parenthetical_variants(raw_name: str) -> set[str]:
    raw_name = (raw_name or "").strip()
    variants = {raw_name}
    pattern = re.compile(r"^\s*([^()]+?)\s*\(([^()]+)\)\s*$")
    match = pattern.match(raw_name)
    if not match:
        return variants

    left = match.group(1).strip()
    inner = match.group(2).strip()
    if left:
        variants.add(left)
    if inner:
        variants.add(inner)
    if left and inner:
        variants.add(f"{left} {inner}")
        variants.add(f"{left} + {inner}")
    return variants


def _expand_variants(raw_name: str) -> set[str]:
    variants: set[str] = set()
    for item in _parenthetical_variants(raw_name):
        variants.add(item)
        variants.add(item.replace("+", " + "))
        variants.add(item.replace(" + ", " "))
        variants.add(item.replace(" and ", " + "))
    return {v.strip() for v in variants if v.strip()}


@lru_cache(maxsize=1)
def _load_medication_lexicon() -> _MedicationLexicon:
    csv_path = Path(__file__).resolve().parent / "data" / "india_common_medicines_seed_list.csv"
    exact_index: dict[str, str] = {}
    max_words = 1

    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            canonical = (row.get("generic_name_or_common_combination") or "").strip()
            if not canonical:
                continue

            for variant in _expand_variants(canonical):
                normalized = _normalize_for_match(variant)
                if not normalized:
                    continue
                exact_index.setdefault(normalized, canonical)
                max_words = max(max_words, len(normalized.split()))

    return _MedicationLexicon(
        exact_index=exact_index,
        normalized_keys=list(exact_index.keys()),
        max_words=min(max_words, MAX_NGRAM_WORDS),
    )


def _extract_line_phrases(text: str, max_words: int) -> list[str]:
    phrases: list[str] = []
    for line in (text or "").splitlines():
        tokens = re.findall(r"[A-Za-z0-9+]+", line)
        if not tokens:
            continue

        tokens_lower = [token.lower() for token in tokens]
        token_count = len(tokens_lower)
        upper = min(max_words, token_count)

        for size in range(upper, 0, -1):
            for idx in range(0, token_count - size + 1):
                phrase = " ".join(tokens_lower[idx: idx + size])
                normalized = _normalize_for_match(phrase)
                if normalized:
                    phrases.append(normalized)
    return phrases


def _token_length(text: str) -> int:
    if not text:
        return 0
    return len(text.split())


def _match_exact_db(candidates: list[str], lexicon: _MedicationLexicon) -> MedicationMatch | None:
    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        canonical = lexicon.exact_index.get(candidate)
        if canonical:
            confidence = 1.0 if _token_length(candidate) > 1 else 0.99
            return MedicationMatch(canonical, confidence, "exact_db")
    return None


def _match_fuzzy_db(
    candidates: list[str],
    lexicon: _MedicationLexicon,
    cutoff: float = FUZZY_MATCH_THRESHOLD,
) -> MedicationMatch | None:
    best: tuple[float, str] | None = None
    seen: set[str] = set()

    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if len(candidate) < MIN_WORD_LEN:
            continue

        matches = get_close_matches(
            candidate,
            lexicon.normalized_keys,
            n=1,
            cutoff=cutoff,
        )
        if not matches:
            continue

        chosen = matches[0]
        candidate_words = _token_length(candidate)
        chosen_words = _token_length(chosen)
        if abs(candidate_words - chosen_words) > 1:
            continue

        similarity = SequenceMatcher(None, candidate, chosen).ratio()
        if best is None or similarity > best[0]:
            best = (similarity, chosen)

    if best is None:
        return None

    similarity, normalized_match = best
    canonical = lexicon.exact_index[normalized_match]
    return MedicationMatch(canonical, min(0.98, similarity), "fuzzy_db")


def _has_med_affix(word: str) -> bool:
    lower = (word or "").lower()
    return any(lower.startswith(prefix) for prefix in MED_PREFIXES) or any(
        lower.endswith(suffix) for suffix in MED_SUFFIXES
    )


def search_medicine_name_by_affix(text: str) -> str | None:
    tokens = re.findall(r"[A-Za-z]{" + str(MIN_WORD_LEN) + r",}", text or "")
    for token in tokens:
        if _has_med_affix(token):
            return token
    return None


def search_medicine_name_by_ip(text: str) -> str | None:
    match = re.search(r"([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+IP\b", text or "")
    if match:
        return match.group(1).strip()
    return None


def _heuristic_candidate(text: str) -> str | None:
    ip_result = search_medicine_name_by_ip(text)
    if ip_result:
        return ip_result
    return search_medicine_name_by_affix(text)


def match_medication_name(text: str) -> MedicationMatch:
    lexicon = _load_medication_lexicon()
    candidates = _extract_line_phrases(text, max_words=lexicon.max_words)

    exact_match = _match_exact_db(candidates, lexicon)
    if exact_match:
        return exact_match

    fuzzy_match = _match_fuzzy_db(candidates, lexicon)
    if fuzzy_match:
        return fuzzy_match

    heuristic = _heuristic_candidate(text)
    if heuristic:
        normalized_heuristic = _normalize_for_match(heuristic)
        canonical = lexicon.exact_index.get(normalized_heuristic)
        if canonical:
            return MedicationMatch(canonical, 0.85, "heuristic_verified")

        fuzzy_heuristic = _match_fuzzy_db([normalized_heuristic], lexicon, cutoff=0.90)
        if fuzzy_heuristic:
            return MedicationMatch(
                medication_name=fuzzy_heuristic.medication_name,
                confidence=min(0.84, fuzzy_heuristic.confidence),
                source="heuristic_verified",
            )
        return MedicationMatch("Not Found", 0.0, "heuristic_unverified")

    return MedicationMatch("Not Found", 0.0, "heuristic_unverified")


def select_best_medication_match(ocr_candidates: list[OCRMedicationCandidate]) -> MedicationMatch:
    best_score: tuple[float, float] = (-1.0, -1.0)
    best_match = MedicationMatch("Not Found", 0.0, "heuristic_unverified")

    for candidate in ocr_candidates:
        match = match_medication_name(candidate.text)
        score = (float(match.confidence), float(candidate.ocr_confidence))
        if score > best_score:
            best_score = score
            best_match = match

    return best_match


def search_medicine_name_first_line(text: str) -> str | None:
    # Backward-compatible function name; now returns DB-backed medication match only.
    matched = match_medication_name(text)
    if matched.medication_name == "Not Found":
        return None
    return matched.medication_name
