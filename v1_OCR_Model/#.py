# Import Libraries
import cv2
from preprocessing.apply_all_preprocessing import apply_all_preprocesses

#image_paths = ['images/pillblisterwhite.png','images/pillblistertin.png'...] img_list = [cv2.imgread(image_path) for image_path in image_paths]
#img_list = [img1, img2, img3...] [apply_all_processing(img) for img in img_list]

# Open images using OpenCV (NOT PIL)
img1 = cv2.imread("images/pillblisterwhite.png")
#img2 = cv2.imread("images/pillblistertin.png")
#img3 = cv2.imread("images/ErythromycinTin.png")
#img4 = cv2.imread("images/IbuprofenTin.png")
#img5 = cv2.imread("images/ParcetamolTin.png")
#img6 = cv2.imread("images/Atorvastatin.png")
#img7 = cv2.imread("images/atorvastatin2.png")
#img8 = cv2.imread("images/amoxycillin.png")
#img9 = cv2.imread("images/amoxycillin2.png")

# Finding the best preprocessing techniques


apply_all_preprocesses(img1)
# apply_all_preprocesses(img2)
# apply_all_preprocesses(img3)
# apply_all_preprocesses(img4)
# apply_all_preprocesses(img5)
# apply_all_preprocesses(img6)
# apply_all_preprocesses(img7)
# apply_all_preprocesses(img8)
# apply_all_preprocesses(img9)


'''
Try Higher Quality Images
Image 1 : Grayscale + EasyOCR with confidence 0.78
Image 2 : Grayscale + Tesseract with confidence 0.44
Image 3 : Denoised + EasyOCR with confidence 0.52
Image 4 : BGR To RGB + EasyOCR with confidence 0.55
Image 5 : CLAHE + EasyOCR with confidence 0.70
Image 6 : Denoised + EasyOCR with confidence 0.53
Image 7 : Grayscale + EasyOCR with confidence 0.77
Image 8 : Denoised + EasyOCR with confidence 0.48
Image 9 : Denoised + EasyOCR with confidence 0.71

Mean Confidence : 0.6089
Most Common OCR Model : EasyOCR
Most Common Preprocessing : Denoised, Grayscale



Try Lower Quality Images


'''