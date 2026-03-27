import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OCR_ROOT = REPO_ROOT / "v1_OCR_Model"
if str(OCR_ROOT) not in sys.path:
    sys.path.insert(0, str(OCR_ROOT))

from search_text.search_brand import search_brand_name  # noqa: E402


def test_brand_detects_standard_registered_symbol():
    text = "Paracetamol Tablets IP 500 mg Pacimol® 500"
    assert search_brand_name(text) == "Pacimol"


def test_brand_detects_ocr_apostrophe_symbol_corruption():
    text = "Paracetamol Tablets IP 500 mg Pacimol' 500 @Regd: Trade Mark"
    assert search_brand_name(text) == "Pacimol"


def test_brand_lexicon_fuzzy_match_for_minor_ocr_typos():
    text = "Paracetamol Tablets IP 500 mg Pecimol 500"
    assert search_brand_name(text) == "Pacimol"

