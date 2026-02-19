import easyocr
reader = easyocr.Reader(['en'], gpu=False)

def get_easyocr_confidence(image):
    results = reader.readtext(image)

    if not results:
        return 0

    confidences = [res[2] for res in results]
    return sum(confidences) / len(confidences)
