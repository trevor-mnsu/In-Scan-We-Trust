# Import Libraries
import cv2
import pytesseract
from PIL import Image
import re
import matplotlib.pyplot as plt

def phase1(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Print Phase 1 processed image
    plt.imshow(img_rgb, cmap='gray')
    plt.title("Phase 1 Processed Image")
    plt.axis("off")

    # Extract text
    text = pytesseract.image_to_string(img_rgb)
    print("Extracted text:\n", text)
    return(text)