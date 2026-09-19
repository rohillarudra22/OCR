import os
import requests

def extract_text_from_images(front_path, back_path):
    """
    Universal Cloud OCR: Har uploaded image ka live text read karta hai.
    Zero local binary dependency, zero API key requirement.
    """
    extracted_text = []

    def scan_file(file_path):
        if not file_path or not os.path.exists(file_path):
            return ""
        try:
            with open(file_path, 'rb') as f:
                # Free public OCR endpoint (zero token/auth required)
                r = requests.post(
                    'https://api.ocr.space/parse/image',
                    files={'file': f},
                    data={'language': 'eng', 'isOverlayRequired': False},
                    headers={'apikey': 'helloworld'},
                    timeout=20
                )
                if r.status_code == 200:
                    res = r.json()
                    parsed_results = res.get('ParsedResults', [])
                    if parsed_results:
                        return parsed_results[0].get('ParsedText', '').strip()
        except Exception as err:
            print(f"OCR request error on {file_path}: {err}")
        return ""

    # Front aur Back dono packaging images scan hongi
    txt_f = scan_file(front_path)
    txt_b = scan_file(back_path)

    if txt_f:
        extracted_text.append(txt_f)
    if txt_b:
        extracted_text.append(txt_b)

    return "\n".join(extracted_text)