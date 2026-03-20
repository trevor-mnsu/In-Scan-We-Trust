from .bgr_to_rgb import bgr_to_rgb
from .gray_scale import gray_scale
from .mildly_denoised import mildly_denoised
from .illumination_normilization import illumination_normalization
from .clahe import clahe
from .resize_image import resize_image
from evaluate.get_average_confidence import get_average_confidence
from evaluate.get_easyocr_confidence import get_easyocr_confidence
import pytesseract
import easyocr
reader = easyocr.Reader(['en'], gpu=False)

def apply_all_preprocesses(img):

    results = {}

    preprocessing_methods = {
        "BGR To RGB": bgr_to_rgb,
        "Grayscale": gray_scale,
        "Resize" : resize_image,
        "Denoised": mildly_denoised,
        "Illumination Normalized": illumination_normalization,
        "CLAHE": clahe,
    }

    for name, func in preprocessing_methods.items():

        processed_img = func(img)

        # Tesseract
        tess_conf = get_average_confidence(processed_img)
        results[f"{name} + Tesseract"] = (processed_img, tess_conf)

        # EasyOCR
        easy_conf = get_easyocr_confidence(processed_img)
        results[f"{name} + EasyOCR"] = (processed_img, easy_conf)

    # Print all results
    for method, (_, score) in results.items():
        print(f"Average confidence for {method}: {score:.2f}")

    # Pick best overall
    best_method = max(results, key=lambda k: results[k][1])
    best_img, best_score = results[best_method]

    print("\nBest overall pipeline:")
    print(f"{best_method} with confidence {best_score:.2f}")

    if "Tesseract" in best_method:
        best_text = pytesseract.image_to_string(best_img)
    else:
        easy_results = reader.readtext(best_img)
        best_text = " ".join([res[1] for res in easy_results])

    print("\nBest OCR Text:")
    print(best_text)

    return best_img, best_method, best_score, best_text
