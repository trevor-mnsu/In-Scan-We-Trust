"""
Usage:
  python tools/evaluate_brand_extraction.py --images-dir ..\\test_images --ground-truth ..\\ground_truth.csv

ground_truth.csv format:
  filename,expected_brand
  image1.png,Pacimol
"""

import argparse
import csv
import time
from pathlib import Path

from app.services.ocr_service import process_image_bytes


def _normalize(value):
    return (value or "").strip().lower()


def main():
    parser = argparse.ArgumentParser(description="Evaluate brand extraction quality.")
    parser.add_argument("--images-dir", required=True, help="Directory containing test images.")
    parser.add_argument("--ground-truth", required=True, help="CSV with filename,expected_brand columns.")
    parser.add_argument("--output", default=None, help="Optional output CSV path for per-image results.")
    args = parser.parse_args()

    images_dir = Path(args.images_dir).resolve()
    truth_path = Path(args.ground_truth).resolve()
    output_path = Path(args.output).resolve() if args.output else None

    rows = list(csv.DictReader(truth_path.open("r", encoding="utf-8")))
    if not rows:
        raise ValueError("Ground truth CSV is empty.")

    tp = fp = fn = 0
    elapsed = []
    detailed = []

    for row in rows:
        filename = row["filename"].strip()
        expected_brand = row["expected_brand"].strip()
        image_path = images_dir / filename
        if not image_path.exists():
            detailed.append(
                {
                    "filename": filename,
                    "expected_brand": expected_brand,
                    "predicted_brand": "MISSING_FILE",
                    "match": "error",
                    "latency_seconds": "",
                    "confidence": "",
                    "best_method": "",
                }
            )
            continue

        start = time.perf_counter()
        result = process_image_bytes(image_path.read_bytes())
        latency_seconds = time.perf_counter() - start
        elapsed.append(latency_seconds)

        predicted_brand = result.extracted_fields.get("brand_name", "Not Found")
        predicted_norm = _normalize(predicted_brand)
        expected_norm = _normalize(expected_brand)

        is_found = predicted_norm != "not found"
        is_match = is_found and predicted_norm == expected_norm

        if is_match:
            tp += 1
            verdict = "tp"
        elif is_found:
            fp += 1
            verdict = "fp"
        else:
            fn += 1
            verdict = "fn"

        detailed.append(
            {
                "filename": filename,
                "expected_brand": expected_brand,
                "predicted_brand": predicted_brand,
                "match": verdict,
                "latency_seconds": f"{latency_seconds:.3f}",
                "confidence": f"{result.overall_confidence:.3f}",
                "best_method": result.best_method,
            }
        )

    precision = (tp / (tp + fp)) if (tp + fp) else 0.0
    recall = (tp / (tp + fn)) if (tp + fn) else 0.0
    avg_latency = (sum(elapsed) / len(elapsed)) if elapsed else 0.0

    print("=== Brand Extraction Evaluation ===")
    print(f"Samples: {len(rows)}")
    print(f"TP: {tp} | FP: {fp} | FN: {fn}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"Avg latency (s/image): {avg_latency:.3f}")

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "filename",
                    "expected_brand",
                    "predicted_brand",
                    "match",
                    "latency_seconds",
                    "confidence",
                    "best_method",
                ],
            )
            writer.writeheader()
            writer.writerows(detailed)
        print(f"Detailed results written to: {output_path}")


if __name__ == "__main__":
    main()

