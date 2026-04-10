'''
Resize the image to optimize the resolution for best OCR readings
'''
import cv2


def resize_image(img):
    # resize the image first
    
    height, width = img.shape[:2]
    new_width =1500
    scale_ratio = new_width / width
    new_height = int(height * scale_ratio)
    resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

    return resized_img
    
