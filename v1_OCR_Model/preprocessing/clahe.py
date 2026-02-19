import cv2

from .illumination_normilization import illumination_normalization


def clahe(img):
    # First apply illumination normalization to the image
    processed_img = illumination_normalization(img)

    # Create CLAHE object
    clahe_obj = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    # Apply CLAHE to the processed image
    clahe_img = clahe_obj.apply(processed_img)

    print("CLAHE applied on the processed image.")

    return clahe_img
