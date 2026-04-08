from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ExtractedFields(BaseModel):
    medication_name: str
    brand_name: str
    dose_strength: str


class MedicationRecordOut(BaseModel):
    id: int
    created_at: datetime
    source: str
    status: str
    medicine_name: str
    brand_name: str
    dose_strength: str
    ocr_method: str | None = None
    ocr_confidence: float | None = None
    image_filename: str | None = None
    manual_notes: str | None = None

    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    status: Literal["accepted", "needs_review"]
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    best_method: str
    extracted_fields: ExtractedFields
    missing_fields: list[str]
    review_reason: str | None = None
    record: MedicationRecordOut | None = None


class RecordsResponse(BaseModel):
    records: list[MedicationRecordOut]

