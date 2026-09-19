import re

def parse_metrology_data(raw_text):
    parsed_data = {
        "consumer_care": {"email": None, "phone": None},
        "country_of_origin": None,
        "expiry_date": None,
        "manufacturer_address": None,
        "manufacturer_name": None,
        "mfg_date": None,
        "mrp": None,
        "mrp_inclusive_of_taxes": False,
        "net_quantity": None,
        "quantity_unit": None,
        "raw_text_dump": raw_text
    }

    if not raw_text:
        return parsed_data

    # Universal Email match
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', raw_text)
    if email_match:
        parsed_data["consumer_care"]["email"] = email_match.group(0).strip()

    # Universal Phone / Toll-free match (1800, 1860, landlines, mobile numbers)
    phone_match = re.search(r'(?:(?:1800|1860)[\s\-]?[0-9]{2,4}[\s\-]?[0-9]{3,4})|(?:\+?91[\s\-]?[6-9]\d{9})|(?:\b[0-9]{3,5}[\s\-]?[0-9]{6,8}\b)', raw_text)
    if phone_match:
        parsed_data["consumer_care"]["phone"] = phone_match.group(0).strip()

    # MRP match
    mrp_match = re.search(r'(?:MRP|Rs\.?|₹)\s*[:\-]?\s*([0-9]+(?:\.[0-9]{1,2})?)', raw_text, re.IGNORECASE)
    if mrp_match:
        parsed_data["mrp"] = float(mrp_match.group(1))
        parsed_data["mrp_inclusive_of_taxes"] = "tax" in raw_text.lower() or "incl" in raw_text.lower()

    # Net Quantity & Unit (g, ml, kg, etc.)
    qty_match = re.search(r'(?:Net\s*(?:Quantity|Qty|Weight|Wt|Volume)|Weight)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]+)', raw_text, re.IGNORECASE)
    if qty_match:
        parsed_data["net_quantity"] = qty_match.group(1)
        parsed_data["quantity_unit"] = qty_match.group(2)

    # Country of origin
    if "india" in raw_text.lower():
        parsed_data["country_of_origin"] = "India"

    return parsed_data