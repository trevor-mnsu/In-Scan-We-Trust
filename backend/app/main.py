from datetime import datetime
from pathlib import Path
from uuid import uuid4
import os

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import ALLOWED_ORIGINS, UPLOADS_DIR
from .db import Base, engine, get_db
from .models import MedicationRecord
from .schemas import ExtractedFields, MedicationRecordOut, RecordsResponse, ScanResponse
from .services.ocr_service import evaluate_scan_quality, process_image_bytes


app = FastAPI(title="Smart Medicine OCR API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https?://((localhost|127\.0\.0\.1)|((10|172|192)\.\d+\.\d+\.\d+))(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


def _save_upload(image_bytes: bytes, original_filename: str) -> tuple[str, str]:
    suffix = Path(original_filename).suffix.lower() or ".jpg"
    safe_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:8]}{suffix}"
    output_path = UPLOADS_DIR / safe_filename
    output_path.write_bytes(image_bytes)
    return safe_filename, str(output_path)


@app.post("/scan", response_model=ScanResponse)
async def scan_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        ocr_result = process_image_bytes(image_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {exc}") from exc

    quality = evaluate_scan_quality(ocr_result.extracted_fields, ocr_result.overall_confidence)

    extracted = ExtractedFields(
        search_name=ocr_result.extracted_fields.get("search_name", "Not Found"),
        brand_name=ocr_result.extracted_fields.get("brand_name", "Not Found"),
        dose_strength=ocr_result.extracted_fields.get("dose_strength", "Not Found"),
    )

    if quality.status == "needs_review":
        return ScanResponse(
            status="needs_review",
            overall_confidence=ocr_result.overall_confidence,
            best_method=ocr_result.best_method,
            extracted_fields=extracted,
            missing_fields=quality.missing_fields,
            review_reason=quality.reason,
            record=None,
        )

    image_filename, image_path = _save_upload(image_bytes, file.filename or "capture.jpg")
    record = MedicationRecord(
        source="ocr",
        status="accepted",
        medicine_name=extracted.search_name,
        brand_name=extracted.brand_name,
        dose_strength=extracted.dose_strength,
        ocr_method=ocr_result.best_method,
        ocr_confidence=ocr_result.overall_confidence,
        ocr_text=ocr_result.raw_text,
        image_filename=image_filename,
        image_path=image_path,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ScanResponse(
        status="accepted",
        overall_confidence=ocr_result.overall_confidence,
        best_method=ocr_result.best_method,
        extracted_fields=extracted,
        missing_fields=[],
        review_reason=None,
        record=MedicationRecordOut.model_validate(record),
    )


@app.post("/manual", response_model=MedicationRecordOut)
async def save_manual_record(
    medicine_name: str = Form(...),
    brand_name: str = Form(...),
    dose_strength: str = Form(...),
    manual_notes: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
):
    if not medicine_name.strip() or not brand_name.strip() or not dose_strength.strip():
        raise HTTPException(status_code=400, detail="Medicine name, brand name, and dose strength are required.")

    image_filename = None
    image_path = None
    if file is not None:
        image_bytes = await file.read()
        if image_bytes:
            image_filename, image_path = _save_upload(image_bytes, file.filename or "manual.jpg")

    record = MedicationRecord(
        source="manual",
        status="manual",
        medicine_name=medicine_name.strip(),
        brand_name=brand_name.strip(),
        dose_strength=dose_strength.strip(),
        ocr_method=None,
        ocr_confidence=None,
        ocr_text=None,
        image_filename=image_filename,
        image_path=image_path,
        manual_notes=(manual_notes or "").strip() or None,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return MedicationRecordOut.model_validate(record)


@app.get("/records", response_model=RecordsResponse)
def list_records(db: Session = Depends(get_db)):
    records = db.query(MedicationRecord).order_by(MedicationRecord.created_at.desc()).all()
    return RecordsResponse(records=[MedicationRecordOut.model_validate(row) for row in records])


@app.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(MedicationRecord).filter(MedicationRecord.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found.")

    if record.image_path:
        try:
            if os.path.exists(record.image_path):
                os.remove(record.image_path)
        except OSError:
            # Keep delete resilient even if image cleanup fails.
            pass

    db.delete(record)
    db.commit()
    return {"status": "deleted", "id": record_id}
