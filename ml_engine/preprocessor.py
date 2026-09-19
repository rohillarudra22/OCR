import cv2
import numpy as np

def clean_and_normalize_image(image_path: str, max_dim: int = 1600) -> np.ndarray:
    """Loads, resizes, and enhances packaging images for higher OCR recognition accuracy.
    Handles glossy surfaces, varying contrasts, and skewed labels.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image could not be loaded from path: {image_path}")

    # 1. Resize if image is too large (maintains aspect ratio while saving GPU/CPU memory)
    height, width = img.shape[:2]
    if max(height, width) > max_dim:
        scale = max_dim / max(height, width)
        img = cv2.resize(img, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)

    # 2. Increase local contrast to make small printed text (like MRP/Mfg Date) stand out
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)
    merged = cv2.merge((cl, a_channel, b_channel))
    enhanced_bgr = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

    # 3. Return RGB format as required by keras-ocr
    return cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)