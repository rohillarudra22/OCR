import os
import cv2
import numpy as np
import pytesseract

# Windows par Tesseract installation path check
tesseract_cmd_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(tesseract_cmd_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

def clean_and_enhance_image(image_path):
    """
    Advanced OpenCV preprocessing pipeline specifically tuned
    for curved, glossy, and low-contrast packaging panels.
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    # 1. Image Resolution Check & Auto-Upscaling
    # Chote statutory text (batch no, MRP) ko enlarge karna
    h, w = img.shape[:2]
    if w < 1200:
        scaling_factor = 1400.0 / float(w)
        img = cv2.resize(img, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_CUBIC)

    # 2. Grayscale Conversion
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. CLAHE (Glare aur uneven lighting balance karne ke liye)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_balanced = clahe.apply(gray)

    # 4. Bilateral Filtering (Noise remove karta hai par text edges sharp rehte hain)
    denoised = cv2.bilateralFilter(contrast_balanced, d=9, sigmaColor=75, sigmaSpace=75)

    # 5. Adaptive Gaussian Thresholding (Text aur colored background ko cleanly split karna)
    binarized = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 9
    )

    return binarized

def extract_text_from_images(front_path, back_path):
    """
    Preprocesses both packaging panels and extracts bilingual text using Tesseract 5.
    """
    front_clean = clean_and_enhance_image(front_path)
    back_clean = clean_and_enhance_image(back_path)

    # PSM 3: Automatic Page Segmentation (packaging blocks ke liye best)
    # eng+hin: English aur Hindi Devanagari dono read karne ke liye
    custom_config = r'--oem 3 --psm 3 -l eng+hin'

    front_text = ""
    back_text = ""

    if front_clean is not None:
        front_text = pytesseract.image_to_string(front_clean, config=custom_config)

    if back_clean is not None:
        back_text = pytesseract.image_to_string(back_clean, config=custom_config)

    return front_text, back_text