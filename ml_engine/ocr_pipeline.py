import os
import google.generativeai as genai
from PIL import Image

# Google AI Studio se free API key (https://aistudio.google.com/)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def extract_text_from_images(front_path, back_path):
    """
    Real-time vision extraction jo kisi bhi product label ka 
    100% genuine text, phone number, address, aur MRP nikalta hai.
    """
    try:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY missing in environment")

        model = genai.GenerativeModel("gemini-1.5-flash")

        front_img = Image.open(front_path)
        back_img = Image.open(back_path)

        prompt = (
            "Extract all text verbatim from these two package images (front and back). "
            "Specifically ensure you transcribe the legal metrology details: "
            "Commodity name, Net Quantity/Weight, Maximum Retail Price (MRP), "
            "Month and Year of Manufacture/Packing, Expiry/Best Before date, "
            "Full manufacturer/packer name and address, customer care email, and customer care phone number."
        )

        response = model.generate_content([prompt, front_img, back_img])
        return response.text.strip()

    except Exception as e:
        print(f"Dynamic OCR pipeline error: {e}")
        return ""