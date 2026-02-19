# Import Libraries
import cv2
from preprocessing.apply_all_preprocessing import apply_all_preprocesses

# Open images using OpenCV (NOT PIL)
img1 = cv2.imread("v1_OCR_Model/images/pillblisterwhite.png")
img2 = cv2.imread("v1_OCR_Model/images/pillblistertin.png")

# Finding the best preprocessing techniques
apply_all_preprocesses(img2)

