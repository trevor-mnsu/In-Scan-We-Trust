# Import Libraries
import cv2
from pathlib import Path
from preprocessing.apply_all_preprocessing import apply_all_preprocesses
from search_text.search_text import search_text

#image_paths = ['images/pillblisterwhite.png','images/pillblistertin.png'...] img_list = [cv2.imgread(image_path) for image_path in image_paths]
#img_list = [img1, img2, img3...] [apply_all_processing(img) for img in img_list]

# Open images using OpenCV (NOT PIL)
base_dir = Path(__file__).resolve().parent
images_dir = base_dir / "images"

image_paths = [
    #str(images_dir / "pillblisterwhite.png"),
    #str(images_dir / "pillblistertin.png"),
    #str(images_dir / "ParcetamolTin.png"),
    #str(images_dir / "IbuprofenTin.png"),
    #str(images_dir / "ErythromycinTin.png"),
    str(images_dir / "Atorvastatin.png"),
    #str(images_dir / "atorvastatin2.png"),
    #str(images_dir / "amoxycillin2.png"),
    #str(images_dir / "amoxycillin2.png"),
]

# Finding the best preprocessing techniques
for path in image_paths:
    img = cv2.imread(path)
    if img is None:
        print(f"\n--- {path} --- SKIPPED (file not found)")
        continue
    print(f"\n--- {path} ---")
    _, _, _, best_text, _ = apply_all_preprocesses(img)
    print(search_text(best_text))



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
