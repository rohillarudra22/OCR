import base64
import os
import requests

def extract_text_from_images(front_path, back_path):
    """
    100% dynamic vision OCR: Seedha image ke pixels padhega, 
    kisi bhi naye packet ka real printed text extract karega.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        api_key = "AQ.Ab8RN6KTUoDMEX5dX59yGNfXFRKNhEoR9Z6Ahx6vy7zKvyLQ0Q"

    try:
        def to_b64(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")

        front_b64 = to_b64(front_path)
        back_b64 = to_b64(back_path)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}

        prompt = (
            "You are an optical character recognition engine. "
            "Read and transcribe EVERY printed word and number from both images verbatim. "
            "Do not summarize. Extract all details: product name, net quantity, "
            "MRP, dates (mfg, expiry, use by), manufacturer name and address, "
            "and all consumer care contact numbers, toll-free numbers, and emails."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": front_b64
                            }
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": back_b64
                            }
                        }
                    ]
                }
            ]
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code == 200:
            res_json = resp.json()
            candidates = res_json.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
        else:
            print(f"Gemini API error status: {resp.status_code}, response: {resp.text}")

    except Exception as e:
        print(f"Extraction error: {e}")

    return ""