# Import Libraries
from pathlib import Path

import cv2

from preprocessing.apply_all_preprocessing import apply_all_preprocesses
from search_text.search_text import search_text


def load_image(image_path: Path):
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
    return img


# Resolve image paths relative to this script so it works from any terminal location.
BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"

img1 = load_image(IMAGES_DIR / "pillblisterwhite.png")
img2 = load_image(IMAGES_DIR / "pillblistertin.png")

# Finding the best preprocessing techniques
best_img, best_method, best_score, best_text, _ = apply_all_preprocesses(img1)

# Extract structured fields from the best OCR output and print to terminal.
parsed = search_text(best_text)

print("\nExtracted Fields:")
print(f"Drug Name: {parsed['medication_name']}")
print(f"Brand Name: {parsed['brand_name']}")
print(f"Dose Strength: {parsed['dose_strength']}")


'''
Try Higher Quality Images
Image 1 : Grayscale + EasyOCR with confidence 0.78
Image 2 : Grayscale + Tesseract with confidence 0.44
Image 3 : Denoised + EasyOCR with confidence 0.52
Image 4 : BGR To RGB + EasyOCR with confidence 0.55
Image 5 : CLAHE + EasyOCR with confidence 0.70
Image 6 : Denoised + EasyOCR with confidence 0.53
Image 7 : Grayscale + EasyOCR with confidence 0.77
Image 8 : Denoised + EasyOCR with confidence 0.48
Image 9 : Denoised + EasyOCR with confidence 0.71

Mean Confidence : 0.6089
Most Common OCR Model : EasyOCR
Most Common Preprocessing : Denoised, Grayscale



Try Lower Quality Images


'''
