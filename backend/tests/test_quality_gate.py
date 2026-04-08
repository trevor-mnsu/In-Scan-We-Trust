from app.services.ocr_service import evaluate_scan_quality


def test_quality_gate_accepts_complete_high_confidence():
    fields = {
        "search_name": "Paracetamol",
        "brand_name": "Tylenol",
        "dose_strength": "500 mg",
    }
    result = evaluate_scan_quality(fields, 0.86)
    assert result.status == "accepted"
    assert result.missing_fields == []
    assert result.reason is None


def test_quality_gate_blocks_low_confidence():
    fields = {
        "search_name": "Paracetamol",
        "brand_name": "Tylenol",
        "dose_strength": "500 mg",
    }
    result = evaluate_scan_quality(fields, 0.45)
    assert result.status == "needs_review"
    assert "below threshold" in (result.reason or "")


def test_quality_gate_blocks_missing_required_fields():
    fields = {
        "search_name": "Not Found",
        "brand_name": "Tylenol",
        "dose_strength": "Not Found",
    }
    result = evaluate_scan_quality(fields, 0.92)
    assert result.status == "needs_review"
    assert "search_name" in result.missing_fields
    assert "dose_strength" in result.missing_fields

