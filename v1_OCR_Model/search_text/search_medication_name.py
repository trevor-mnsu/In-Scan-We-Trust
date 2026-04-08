import re
#Note a lot of them have IP indian pharma... look for this?
# Common pharmaceutical prefixes and suffixes used in generic drug naming
# Prefixes often indicate drug class or mechanism of action
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

# Suffixes often indicate drug class
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

# Minimum word length to avoid false positives on short tokens
MIN_WORD_LEN = 4


def _has_med_affix(word):
    """Return True if word starts or ends with a known pharmaceutical affix."""
    w = word.lower()
    for prefix in MED_PREFIXES:
        if w.startswith(prefix):
            return True
    for suffix in MED_SUFFIXES:
        if w.endswith(suffix):
            return True
    return False


def search_medicine_name_by_affix(text):
    """
    Scans all words in the text for known pharmaceutical prefixes/suffixes
    and returns the first matching candidate.

    Returns the matched word (preserving original casing) or None.
    """
    # Tokenise: keep only alphabetic tokens long enough to be a drug name
    tokens = re.findall(r"[A-Za-z]{" + str(MIN_WORD_LEN) + r",}", text)

    for token in tokens:
        if _has_med_affix(token):
            return token

    return None


def search_medicine_name_by_ip(text):
    """
    Looks for 'IP' (Indian Pharmacopoeia) marker and returns the word(s)
    immediately before it, which is typically the generic drug name.

    e.g. "Paracetamol Tablets IP 500 mg" -> "Paracetamol Tablets"
    """
    match = re.search(r"([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+IP\b", text)
    if match:
        return match.group(1).strip()
    return None


def search_medicine_name_first_line(text):
    """
    Tries to find the medicine name using three strategies in order:
      1. IP marker backtrack (Indian Pharmacopoeia).
      2. Affix-based scan across the full text.
      3. Falls back to the first non-empty line.

    Returns a string or None.
    """
    # Strategy 1: IP marker
    ip_result = search_medicine_name_by_ip(text)
    if ip_result:
        return ip_result

    # Strategy 2: prefix/suffix heuristic
    affix_result = search_medicine_name_by_affix(text)
    if affix_result:
        return affix_result

    # Strategy 3: first non-empty line fallback
    lines = text.strip().splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped:
            return stripped

    return None
