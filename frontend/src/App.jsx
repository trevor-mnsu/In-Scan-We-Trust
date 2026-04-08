import { useEffect, useMemo, useState } from "react";
import { deleteRecord, getRecords, saveManualRecord, scanImage } from "./api";

function confidenceLabel(value) {
  const pct = Math.round(value * 100);
  if (pct >= 85) return { text: `${pct}% strong`, tone: "good" };
  if (pct >= 60) return { text: `${pct}% moderate`, tone: "warn" };
  return { text: `${pct}% low`, tone: "bad" };
}

function recordBadgeClass(status) {
  if (status === "accepted") return "badge badge-good";
  if (status === "manual") return "badge badge-warn";
  return "badge";
}

export default function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [isImageViewerOpen, setIsImageViewerOpen] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [records, setRecords] = useState([]);
  const [scanBusy, setScanBusy] = useState(false);
  const [manualBusy, setManualBusy] = useState(false);
  const [deleteBusyId, setDeleteBusyId] = useState(null);
  const [error, setError] = useState("");
  const [manualForm, setManualForm] = useState({
    medicine_name: "",
    brand_name: "",
    dose_strength: "",
    manual_notes: ""
  });

  const confidence = useMemo(() => {
    if (!scanResult) return null;
    return confidenceLabel(scanResult.overall_confidence || 0);
  }, [scanResult]);

  async function loadRecords() {
    try {
      const data = await getRecords();
      setRecords(data);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadRecords();
  }, []);

  useEffect(() => {
    if (!file) {
      setPreviewUrl("");
      return;
    }
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [file]);

  useEffect(() => {
    if (!isImageViewerOpen) return;

    function onKeyDown(event) {
      if (event.key === "Escape") {
        setIsImageViewerOpen(false);
      }
    }

    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [isImageViewerOpen]);

  function onSelectFile(event) {
    const selected = event.target.files?.[0];
    if (!selected) return;
    setError("");
    setScanResult(null);
    setFile(selected);
  }

  async function onRunScan() {
    if (!file) {
      setError("Select or capture a blister image first.");
      return;
    }
    setScanBusy(true);
    setError("");
    try {
      const result = await scanImage(file);
      setScanResult(result);
      if (result.status === "needs_review") {
        setManualForm((prev) => ({
          ...prev,
          medicine_name:
            result.extracted_fields?.search_name !== "Not Found"
              ? result.extracted_fields.search_name
              : "",
          brand_name:
            result.extracted_fields?.brand_name !== "Not Found"
              ? result.extracted_fields.brand_name
              : "",
          dose_strength:
            result.extracted_fields?.dose_strength !== "Not Found"
              ? result.extracted_fields.dose_strength
              : ""
        }));
      } else {
        await loadRecords();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setScanBusy(false);
    }
  }

  async function onManualSubmit(event) {
    event.preventDefault();
    setManualBusy(true);
    setError("");
    try {
      await saveManualRecord({ ...manualForm, file });
      setScanResult(null);
      setManualForm({
        medicine_name: "",
        brand_name: "",
        dose_strength: "",
        manual_notes: ""
      });
      await loadRecords();
    } catch (err) {
      setError(err.message);
    } finally {
      setManualBusy(false);
    }
  }

  function resetCapture() {
    setScanResult(null);
    setFile(null);
    setIsImageViewerOpen(false);
    setManualForm({
      medicine_name: "",
      brand_name: "",
      dose_strength: "",
      manual_notes: ""
    });
  }

  async function onDeleteRecord(recordId) {
    const ok = window.confirm("Delete this record? This cannot be undone.");
    if (!ok) return;

    setDeleteBusyId(recordId);
    setError("");
    try {
      await deleteRecord(recordId);
      await loadRecords();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeleteBusyId(null);
    }
  }

  return (
    <div className="page-shell">
      <div className="bg-shape bg-shape-a" />
      <div className="bg-shape bg-shape-b" />

      <main className="container">
        <header className="hero">
          <h1>Smart Medicine Blister Scanner</h1>
          <p>
            Capture blister sheets, run OCR confidence checks, and only store
            trusted medication records.
          </p>
        </header>

        <section className="panel capture-panel">
          <h2>1. Capture Or Upload</h2>
          <label className="file-input">
            <span>{file ? "Replace Image" : "Take Photo / Choose Image"}</span>
            <input
              type="file"
              accept="image/*"
              capture="environment"
              onChange={onSelectFile}
            />
          </label>

          {previewUrl ? (
            <div className="preview-wrap">
              <button
                type="button"
                className="preview-button"
                onClick={() => setIsImageViewerOpen(true)}
                aria-label="Open full-screen image preview"
              >
                <img src={previewUrl} alt="Selected blister sheet" />
              </button>
            </div>
          ) : (
            <p className="muted">
              Tip: On mobile, this opens your camera directly with rear-lens
              preference.
            </p>
          )}

          <div className="actions">
            <button className="btn btn-primary" onClick={onRunScan} disabled={scanBusy}>
              {scanBusy ? "Scanning..." : "Run OCR Scan"}
            </button>
            <button className="btn btn-ghost" onClick={resetCapture}>
              Clear
            </button>
          </div>
        </section>

        {scanResult && (
          <section className="panel">
            <div className="panel-head">
              <h2>2. Scan Review</h2>
              {confidence && (
                <span className={`badge badge-${confidence.tone}`}>
                  Confidence: {confidence.text}
                </span>
              )}
            </div>

            <div className="fields-grid">
              <div className="field-card">
                <label>Medicine Name</label>
                <p>{scanResult.extracted_fields.search_name}</p>
              </div>
              <div className="field-card">
                <label>Brand Name</label>
                <p>{scanResult.extracted_fields.brand_name}</p>
              </div>
              <div className="field-card">
                <label>Dose Strength</label>
                <p>{scanResult.extracted_fields.dose_strength}</p>
              </div>
            </div>

            <p className="muted">Best OCR pipeline: {scanResult.best_method}</p>

            {scanResult.status === "accepted" ? (
              <div className="notice notice-good">
                OCR passed quality checks and has been saved to the database.
              </div>
            ) : (
              <div className="notice notice-warn">
                <strong>Quality Gate Triggered:</strong> {scanResult.review_reason}
                <br />
                Retake the photo or enter the details manually before saving.
              </div>
            )}
          </section>
        )}

        {scanResult?.status === "needs_review" && (
          <section className="panel manual-panel">
            <h2>3. Manual Entry Required</h2>
            <form onSubmit={onManualSubmit}>
              <label>
                Medicine Name
                <input
                  value={manualForm.medicine_name}
                  onChange={(e) =>
                    setManualForm((prev) => ({ ...prev, medicine_name: e.target.value }))
                  }
                  required
                />
              </label>
              <label>
                Brand Name
                <input
                  value={manualForm.brand_name}
                  onChange={(e) =>
                    setManualForm((prev) => ({ ...prev, brand_name: e.target.value }))
                  }
                  required
                />
              </label>
              <label>
                Dose Strength
                <input
                  value={manualForm.dose_strength}
                  onChange={(e) =>
                    setManualForm((prev) => ({ ...prev, dose_strength: e.target.value }))
                  }
                  required
                />
              </label>
              <label>
                Notes (optional)
                <textarea
                  value={manualForm.manual_notes}
                  onChange={(e) =>
                    setManualForm((prev) => ({ ...prev, manual_notes: e.target.value }))
                  }
                  rows={3}
                />
              </label>

              <div className="actions">
                <button className="btn btn-primary" type="submit" disabled={manualBusy}>
                  {manualBusy ? "Saving..." : "Save Manual Record"}
                </button>
                <button className="btn btn-ghost" type="button" onClick={resetCapture}>
                  Retake Instead
                </button>
              </div>
            </form>
          </section>
        )}

        <section className="panel">
          <div className="panel-head">
            <h2>Dashboard</h2>
            <button className="btn btn-ghost" onClick={loadRecords}>
              Refresh
            </button>
          </div>

          {records.length === 0 ? (
            <p className="muted">No records yet. Run your first scan above.</p>
          ) : (
            <div className="records-list">
              {records.map((record) => (
                <article key={record.id} className="record-item">
                  <div className="record-row">
                    <h3>Record #{record.id}</h3>
                    <span className={recordBadgeClass(record.status)}>{record.status}</span>
                  </div>
                  <p>
                    <strong>Medicine:</strong> {record.medicine_name}
                  </p>
                  <p>
                    <strong>Brand:</strong> {record.brand_name}
                  </p>
                  <p>
                    <strong>Dose:</strong> {record.dose_strength}
                  </p>
                  <p className="muted">
                    Source: {record.source}
                    {record.ocr_confidence != null ? ` | OCR ${Math.round(record.ocr_confidence * 100)}%` : ""}
                  </p>
                  <div className="record-actions">
                    <button
                      className="btn btn-danger"
                      type="button"
                      onClick={() => onDeleteRecord(record.id)}
                      disabled={deleteBusyId === record.id}
                    >
                      {deleteBusyId === record.id ? "Deleting..." : "Delete"}
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        {error && <div className="error-banner">{error}</div>}
      </main>

      {isImageViewerOpen && previewUrl && (
        <div
          className="image-modal"
          role="dialog"
          aria-modal="true"
          aria-label="Full-screen blister image preview"
          onClick={() => setIsImageViewerOpen(false)}
        >
          <button
            type="button"
            className="image-modal-close"
            onClick={() => setIsImageViewerOpen(false)}
            aria-label="Close full-screen preview"
          >
            Close
          </button>
          <img
            className="image-modal-content"
            src={previewUrl}
            alt="Full-screen selected blister sheet"
            onClick={(event) => event.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
}
