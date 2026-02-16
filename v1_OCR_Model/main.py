# Import Libraries
import cv2
import pytesseract
import re

from phases.phase1 import phase1
from search_text.search_text import search_text

# Open images using OpenCV (NOT PIL)
img1 = cv2.imread("v1_OCR_Model/images/pillblisterwhite.png")
img2 = cv2.imread("v1_OCR_Model/images/pillblistertin.png")

# Try phase 1 
text = phase1(img1)
searched_results = search_text(text)
print(searched_results)