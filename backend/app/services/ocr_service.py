from dataclasses import dataclass
from pathlib import Path
import sys

import cv2
import numpy as np

from ..config import MIN_OCR_CONFIDENCE, REQUIRED_FIELDS


@dataclass
class OCRResult:
    best_method: str
    overall_confidence: float
    raw_text: str
    extracted_fields: dict[str, str]


@dataclass
class QualityCheck:
    status: str
    missing_fields: list[str]
    reason: str | None


def _load_ocr_modules():
    """
    Adds the OCR model folder to sys.path and imports project OCR functions.
    Keeping this lazy avoids expensive OCR imports at module load time.
    """
    repo_root = Path(__file__).resolve().parents[3]
    ocr_root = repo_root / "v1_OCR_Model"
    if not ocr_root.exists():
        # Backward-compatible fallback for alternate workspace layouts.
        ocr_root = repo_root / "In-Scan-We-Trust" / "v1_OCR_Model"
    if not ocr_root.exists():
        raise FileNotFoundError(f"OCR module path not found: {ocr_root}")
    ocr_root_str = str(ocr_root)
    if ocr_root_str not in sys.path:
        sys.path.insert(0, ocr_root_str)

    from preprocessing.apply_all_preprocessing import apply_all_preprocesses  # type: ignore
    from search_text.search_medication_name import OCRMedicationCandidate, select_best_medication_match  # type: ignore
    from search_text.search_text import search_text  # type: ignore

    return apply_all_preprocesses, search_text, OCRMedicationCandidate, select_best_medication_match


def evaluate_scan_quality(extracted_fields: dict[str, str], overall_confidence: float) -> QualityCheck:
    missing_fields = [
        field_name
        for field_name in REQUIRED_FIELDS
        if extracted_fields.get(field_name, "Not Found") == "Not Found"
    ]

    if overall_confidence < MIN_OCR_CONFIDENCE and missing_fields:
        return QualityCheck(
            status="needs_review",
            missing_fields=missing_fields,
            reason=(
                f"OCR confidence is below threshold ({overall_confidence:.2f} < {MIN_OCR_CONFIDENCE:.2f}) "
                f"and required fields are missing."
            ),
        )

    if overall_confidence < MIN_OCR_CONFIDENCE:
        return QualityCheck(
            status="needs_review",
            missing_fields=missing_fields,
            reason=f"OCR confidence is below threshold ({overall_confidence:.2f} < {MIN_OCR_CONFIDENCE:.2f}).",
        )

    if missing_fields:
        return QualityCheck(
            status="needs_review",
            missing_fields=missing_fields,
            reason=f"Required field(s) missing: {', '.join(missing_fields)}.",
        )

    return QualityCheck(status="accepted", missing_fields=[], reason=None)


def process_image_bytes(image_bytes: bytes) -> OCRResult:
    np_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image. Please upload a valid image file.")

    apply_all_preprocesses, search_text, OCRMedicationCandidate, select_best_medication_match = _load_ocr_modules()
    _, best_method, best_score, best_text, all_ocr_outputs = apply_all_preprocesses(image)
    extracted_fields = search_text(best_text)

    medication_candidates = [
        OCRMedicationCandidate(
            method=item.get("method", ""),
            ocr_confidence=float(item.get("ocr_confidence", 0.0)),
            text=item.get("text", ""),
        )
        for item in all_ocr_outputs
    ]
    best_medication_match = select_best_medication_match(medication_candidates)
    extracted_fields["medication_name"] = best_medication_match.medication_name

    return OCRResult(
        best_method=best_method,
        overall_confidence=float(best_score),
        raw_text=best_text,
        extracted_fields=extracted_fields,
    )
