from .bgr_to_rgb import bgr_to_rgb
from .gray_scale import gray_scale
from .mildly_denoised import mildly_denoised
from .illumination_normilization import illumination_normalization
from .clahe import clahe
from evaluate.get_average_confidence import get_average_confidence
from evaluate.get_easyocr_confidence import get_easyocr_confidence
from search_text.search_text import search_text
import pytesseract
import easyocr
reader = easyocr.Reader(['en'], gpu=False)

def apply_all_preprocesses(img):

    results = {}

    preprocessing_methods = {
        "BGR To RGB": bgr_to_rgb,
        "Grayscale": gray_scale,
        "Denoised": mildly_denoised,
        "Illumination Normalized": illumination_normalization,
        "CLAHE": clahe,
    }

    for name, func in preprocessing_methods.items():

        processed_img = func(img)

        # Tesseract
        tess_conf = get_average_confidence(processed_img)
        tess_text = pytesseract.image_to_string(processed_img)
        tess_fields = search_text(tess_text)
        tess_coverage = sum(1 for value in tess_fields.values() if value != "Not Found") / 3.0
        tess_brand_bonus = 1.0 if tess_fields.get("brand_name") != "Not Found" else 0.0
        tess_composite = (0.70 * tess_conf) + (0.20 * tess_coverage) + (0.10 * tess_brand_bonus)
        results[f"{name} + Tesseract"] = (processed_img, tess_conf, tess_text, tess_composite)

        # EasyOCR
        easy_conf = get_easyocr_confidence(processed_img)
        easy_results = reader.readtext(processed_img)
        easy_text = " ".join([res[1] for res in easy_results])
        easy_fields = search_text(easy_text)
        easy_coverage = sum(1 for value in easy_fields.values() if value != "Not Found") / 3.0
        easy_brand_bonus = 1.0 if easy_fields.get("brand_name") != "Not Found" else 0.0
        easy_composite = (0.70 * easy_conf) + (0.20 * easy_coverage) + (0.10 * easy_brand_bonus)
        results[f"{name} + EasyOCR"] = (processed_img, easy_conf, easy_text, easy_composite)

    # Print all results
    for method, (_, score, _, composite) in results.items():
        print(f"Average confidence for {method}: {score:.2f} (composite {composite:.2f})")

    # Pick best overall by composite score to reward field quality and brand detection.
    best_method = max(results, key=lambda k: results[k][3])
    best_img, best_score, best_text, _ = results[best_method]

    print("\nBest overall pipeline:")
    print(f"{best_method} with confidence {best_score:.2f}")

    print("\nBest OCR Text:")
    print(best_text)

    return best_img, best_method, best_score, best_text
