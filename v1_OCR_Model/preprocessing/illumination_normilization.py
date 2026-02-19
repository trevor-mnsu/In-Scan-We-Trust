import cv2
import numpy as np
from .mildly_denoised import mildly_denoised
from skimage.exposure import rescale_intensity



def illumination_normalization(img):
    denoised_img = mildly_denoised(img)
    kernel_size = 101 # this has to be odd
    sigmaX = 1.0

    # Convert to float for accurate calculations
    img_float = denoised_img.astype(np.float32)

    # Apply Gaussian blur to estimate background illumination
    background_illumination = cv2.GaussianBlur(img_float, (kernel_size, kernel_size), sigmaX)

    # Normalize the image (add a small epsilon to avoid division by zero)
    illum_normalized_img = img_float / (background_illumination + 1e-6)

    # Scale back to 0-255 and convert to uint8
    illum_normalized_img = cv2.normalize(illum_normalized_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    print("Illumination normalization applied and image displayed successfully.")


    # Apply percentile-based contrast stretching
    # Compute 2nd and 98th percentiles
    p2, p98 = np.percentile(illum_normalized_img, (2, 98))

    # Rescale intensities to full 0-255 range
    contrast_stretched_img = rescale_intensity(illum_normalized_img, in_range=(p2, p98))
    print(f"Contrast stretching applied: 2nd percentile={p2:.2f}, 98th percentile={p98:.2f}.")

    return contrast_stretched_img