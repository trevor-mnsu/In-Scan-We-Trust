# Import Libraries
import cv2
import pytesseract
from PIL import Image

def bgr_to_rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
