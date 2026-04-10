import cv2

def adaptive_threshold(img):
   
    thresh = cv2.adaptiveThreshold(
        cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        15,
        4
    )
    print("Adaptive threshold applied to the image.")
    return thresh
