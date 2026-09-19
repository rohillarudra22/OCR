import os
import cv2
import pytesseract
import numpy as np

# Set binary path
TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_EXE):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE

# Point TESSDATA_PREFIX to the local project tessdata folder
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOCAL_TESSDATA = os.path.join(PROJECT_ROOT, "tessdata")

if os.path.exists(LOCAL_TESSDATA):
    os.environ["TESSDATA_PREFIX"] = LOCAL_TESSDATA

def preprocess_for_packaging(img: np.ndarray) -> np.ndarray:
    """Resizes and normalizes contrast for label inspection."""
    h, w = img.shape[:2]
    if max(h, w) > 1600:
        scale = 1600 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return enhanced

def extract_text_from_images(image_paths: list) -> str:
    """Extracts text using English + Hindi from the configured tessdata directory."""
    extracted_lines = []

    # Detect whether Hindi model is available
    hin_exists = os.path.exists(os.path.join(LOCAL_TESSDATA, "hin.traineddata"))
    lang = "eng+hin" if hin_exists else "eng"

    for idx, path in enumerate(image_paths):
        extracted_lines.append(f"--- IMAGE {idx + 1} START ---")

        if not os.path.exists(path):
            extracted_lines.append(f"[Error: File not found: {path}]")
            extracted_lines.append(f"--- IMAGE {idx + 1} END ---")
            continue

        img = cv2.imread(path)
        if img is None:
            extracted_lines.append(f"[Error: Unreadable image: {path}]")
            extracted_lines.append(f"--- IMAGE {idx + 1} END ---")
            continue

        processed = preprocess_for_packaging(img)

        # Mode 1: Sparse text mode (catches dispersed fields: MRP, dates, net weight)
        text = pytesseract.image_to_string(processed, lang=lang, config=r'--oem 3 --psm 11').strip()

        # Mode 2: Uniform block mode fallback
        if len(text) < 15:
            text = pytesseract.image_to_string(processed, lang=lang, config=r'--oem 3 --psm 6').strip()

        # Mode 3: Raw image fallback
        if len(text) < 15:
            text = pytesseract.image_to_string(img, lang=lang, config=r'--oem 3 --psm 3').strip()

        for line in text.splitlines():
            cleaned = line.strip()
            if cleaned:
                extracted_lines.append(cleaned)

        extracted_lines.append(f"--- IMAGE {idx + 1} END ---")

    return "\n".join(extracted_lines)