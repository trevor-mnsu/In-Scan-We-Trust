import pytesseract
import numpy as np

def get_average_confidence(image):
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    confidences = [
        int(conf) for conf in data["conf"]
        if conf != "-1"
    ]

    if len(confidences) == 0:
        return 0

    return np.mean(confidences) / 100  # normalize to 0–1 scale