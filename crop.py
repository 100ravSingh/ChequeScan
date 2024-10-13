from PIL import Image
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt


start_x = 1280 - 370
start_y = 720 - 380

def preprocess_image(image):
    # Convert to grayscale
    image = np.array(image.convert('RGB'))
    new_size=(1280,720) # pixel size
    resized_image=cv2.resize(image,new_size)
    cropped_image = resized_image[start_y:700, start_x:1250]
    crop_size = (360,240)
    image =cv2.resize(cropped_image,crop_size)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Adjust contrast and brightness
    alpha = 0.5  # Contrast control (1.0-3.0)
    beta = 40   # Brightness control (0-100)
    adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
    
    # Apply simple thresholding to get a binarized image
    _, binary_image = cv2.threshold(adjusted, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    return binary_image

def sharpen_image(image):
    blurred = cv2.GaussianBlur(image, (0,0), 3)
    sharpened = cv2.addWeighted(image, 1.4, blurred, -0.5, 0)
    return sharpened



