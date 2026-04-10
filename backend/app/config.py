from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "medscan.db"

# OCR safety thresholds
MIN_OCR_CONFIDENCE = 0.60
REQUIRED_FIELDS = ("medication_name", "brand_name", "dose_strength")

# Frontend dev server and common LAN-style testing origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

