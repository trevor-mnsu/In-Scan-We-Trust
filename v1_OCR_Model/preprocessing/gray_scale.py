import cv2

def gray_scale(img):
    # Convert the image to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    print(f"Image loaded and converted to grayscale successfully.")
    
    return img_gray