import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OCR_ROOT = REPO_ROOT / "v1_OCR_Model"
if str(OCR_ROOT) not in sys.path:
    sys.path.insert(0, str(OCR_ROOT))

from search_text.search_medication_name import (  # noqa: E402
    OCRMedicationCandidate,
    match_medication_name,
    select_best_medication_match,
)


def test_medication_exact_db_match_single_ingredient():
    text = "Paracetamol Tablets IP 500 mg"
    result = match_medication_name(text)
    assert result.medication_name == "Paracetamol (Acetaminophen)"
    assert result.source == "exact_db"


def test_medication_parentheses_alias_matches_canonical():
    text = "Contains Acetaminophen 500 mg"
    result = match_medication_name(text)
    assert result.medication_name == "Paracetamol (Acetaminophen)"


def test_medication_combination_match_with_plus():
    text = "Amoxicillin + Clavulanic acid tablets"
    result = match_medication_name(text)
    assert result.medication_name == "Amoxicillin + Clavulanic acid"
    assert result.source == "exact_db"


def test_medication_near_match_is_not_forced_at_high_precision():
    text = "Contains Paracitamole 500 mg"
    result = match_medication_name(text)
    assert result.medication_name == "Not Found"


def test_medication_heuristic_verified_path():
    text = "Label shows amoxicillinip"
    result = match_medication_name(text)
    assert result.medication_name == "Amoxicillin"
    assert result.source == "heuristic_verified"


def test_medication_heuristic_unverified_path_returns_not_found():
    text = "Contains zoldoprim tablets"
    result = match_medication_name(text)
    assert result.medication_name == "Not Found"
    assert result.source == "heuristic_unverified"


def test_select_best_medication_match_across_all_ocr_outputs():
    candidates = [
        OCRMedicationCandidate(
            method="Pipeline A",
            ocr_confidence=0.95,
            text="Unreadable text only",
        ),
        OCRMedicationCandidate(
            method="Pipeline B",
            ocr_confidence=0.62,
            text="Paracetamol Tablets IP 500 mg",
        ),
    ]

    result = select_best_medication_match(candidates)
    assert result.medication_name == "Paracetamol (Acetaminophen)"
    assert result.source == "exact_db"
