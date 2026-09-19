import os
import cv2
import numpy as np
import pytesseract

# Windows fallback path
tesseract_cmd_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(tesseract_cmd_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

def preprocess_for_high_accuracy(image_path):
    """
    Advanced multi-stage pipeline:
    Auto-scaling + CLAHE Denoising + Dual-thresholding
    to handle phone glare, curved surfaces, and tiny statutory text.
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    # 1. High-Resolution Upscaling (phone camera images aur chote text ke liye)
    h, w = img.shape[:2]
    if w < 1200:
        scale = 1400.0 / float(w)
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 2. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. CLAHE (Contrast balance + packet glare remove karna)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 4. Bilateral Filter (Noise clean karega par text edges sharp rakhega)
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)

    # 5. Adaptive Thresholding
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 9
    )

    return thresh

def extract_text_from_images(front_path, back_path):
    """
    Dual-pass bilingual OCR (English + Hindi) with automatic page segmentation.
    """
    front_proc = preprocess_for_high_accuracy(front_path)
    back_proc = preprocess_for_high_accuracy(back_path)

    # PSM 3: fully automatic layout analysis
    ocr_config = r'--oem 3 --psm 3 -l eng+hin'

    front_text = ""
    back_text = ""

    if front_proc is not None:
        front_text = pytesseract.image_to_string(front_proc, config=ocr_config)

    if back_proc is not None:
        back_text = pytesseract.image_to_string(back_proc, config=ocr_config)

    # Accuracy fallback: agar back panel par text kam mila toh PSM 11 (sparse text) se re-scan
    if len(back_text.strip()) < 40 and back_proc is not None:
        fallback_config = r'--oem 3 --psm 11 -l eng+hin'
        back_text += "\n" + pytesseract.image_to_string(back_proc, config=fallback_config)

    return front_text, back_text