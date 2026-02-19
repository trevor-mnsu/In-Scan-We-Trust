import cv2
from .gray_scale import gray_scale

def mildly_denoised(img):
    img_gray = gray_scale(img)

    h = 3
    templateWindowSize = 7
    searchWindowSize = 21

    mildly_denoised_img = cv2.fastNlMeansDenoising(img_gray, None, h, templateWindowSize, searchWindowSize)

    print("Mild denoising applied and image displayed successfully.")

    return mildly_denoised_img