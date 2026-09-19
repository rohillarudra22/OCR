import os
from PIL import Image

def extract_text_from_images(front_path, back_path):
    """
    Real-time dynamic packaging text reader.
    Har image se actual text line-by-line read karta hai.
    """
    extracted_lines = []

    try:
        import pytesseract
        
        # Front panel reading
        if front_path and os.path.exists(front_path):
            img_front = Image.open(front_path)
            txt_front = pytesseract.image_to_string(img_front)
            if txt_front.strip():
                extracted_lines.append(txt_front.strip())

        # Back panel reading
        if back_path and os.path.exists(back_path):
            img_back = Image.open(back_path)
            txt_back = pytesseract.image_to_string(img_back)
            if txt_back.strip():
                extracted_lines.append(txt_back.strip())

    except Exception as e:
        print(f"OCR reading error: {e}")

    return "\n".join(extracted_lines)