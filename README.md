# Smart Medicine OCR Demo

This project now includes:

- Existing OCR pipeline in `In-Scan-We-Trust/v1_OCR_Model`
- New FastAPI backend (`backend/`) for scan + quality gate + database
- New mobile-first React + Vite frontend (`frontend/`) for capture/review/dashboard

## Architecture

1. User captures or uploads blister image in frontend.
2. Frontend calls `POST /scan`.
3. Backend runs OCR pipeline and extraction:
   - preprocessing + OCR model selection
   - field extraction (`medication_name`, `brand_name`, `dose_strength`)
4. Quality gate checks confidence and required fields:
   - If pass: save OCR record to SQLite.
   - If fail: block auto-save and require retake or manual entry.
5. Dashboard loads from `GET /records`.

## Backend Setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Frontend Setup

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

The Vite dev server runs on port `5173` and proxies `/api/*` to backend `127.0.0.1:8000`.

## Test

```powershell
cd backend
.venv\Scripts\Activate.ps1
pytest
```

## Brand Evaluation (Before/After)

1. Prepare dataset:
   - `test_images/` folder
   - `ground_truth.csv` with columns `filename,expected_brand`
2. Run evaluator:

```powershell
cd backend
python tools\evaluate_brand_extraction.py --images-dir ..\test_images --ground-truth ..\ground_truth.csv --output ..\eval_results.csv
```

3. Track these metrics:
   - `Precision`
   - `Recall`
   - `Avg latency (s/image)`

## Phone Testing (Easy Local Demo)

1. Ensure laptop and phone are on the same Wi-Fi.
2. Start backend and frontend as above.
3. Find your laptop IP address (`ipconfig` on Windows).
4. Open on your phone:
   - `http://<YOUR-LAPTOP-IP>:5173`
5. Use the capture button to open mobile camera and scan a blister sheet.

## Important Safety Behavior

- Low confidence or missing required fields trigger `needs_review`.
- In that state, record is **not** auto-saved.
- User must either retake image or submit manual fields.
If PowerShell execution policy blocks `npm`, use `npm.cmd` (as above).
