from search_text.search_brand import search_brand_name
from search_text.search_dose_strength import search_dosage_amount
from search_text.search_name import search_medicine_name
from search_text.text_normalizer import normalize_ocr_text


def search_text(text):
    """
    Runs extraction functions and returns backward-compatible keys.
    Missing values are returned as "Not Found".
    """
    normalized = normalize_ocr_text(text)
    normalized_text = normalized["normalized_text"]
    normalized_lines = normalized["normalized_lines"]

    dosage_amount = search_dosage_amount(
        normalized_text,
        normalized_lines=normalized_lines,
    )
    brand_name = search_brand_name(
        normalized_text,
        normalized_lines=normalized_lines,
    )
    medication_name = search_medicine_name(
        normalized_text,
        normalized_lines=normalized_lines,
    )

    # Keep existing key names used by current callers.
    results = {
        "search_name": medication_name if medication_name else "Not Found",
        "brand_name": brand_name if brand_name else "Not Found",
        "dose_strength": dosage_amount if dosage_amount else "Not Found",
    }

    return results
