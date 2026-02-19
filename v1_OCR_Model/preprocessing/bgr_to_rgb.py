# Import Libraries
import cv2
from PIL import Image

def bgr_to_rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
