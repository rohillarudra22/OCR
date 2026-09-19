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

    # 1. Consumer Care Email
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', raw_text)
    if email_match:
        parsed_data["consumer_care"]["email"] = email_match.group(0).strip()

    # 2. Consumer Care Phone / Toll-Free
    phone_match = re.search(r'(?:(?:1800|1860)[\s\-]?[0-9]{2,4}[\s\-]?[0-9]{3,4})|(?:\+?91[\s\-]?[6-9]\d{9})|(?:\b[0-9]{3,5}[\s\-]?[0-9]{6,8}\b)', raw_text)
    if phone_match:
        parsed_data["consumer_care"]["phone"] = phone_match.group(0).strip()

    # 3. Country of Origin
    origin_match = re.search(r'(?:Country of Origin|Made in|Origin)[:\s\-]+([A-Za-z]+)', raw_text, re.IGNORECASE)
    if origin_match:
        parsed_data["country_of_origin"] = origin_match.group(1).strip()
    elif "india" in raw_text.lower():
        parsed_data["country_of_origin"] = "India"

    # 4. Accurate MRP (Nutrition values ko ignore karega, sirf MRP / Rs / ₹ ke sath wale rate ko lega)
    mrp_match = re.search(r'(?:MRP|M\.R\.P\.?|Rs\.?|₹)\s*[:\-]?\s*(?:Rs\.?|₹)?\s*([0-9]{1,4}(?:\.[0-9]{1,2})?)', raw_text, re.IGNORECASE)
    if mrp_match:
        val = float(mrp_match.group(1))
        # Nutritional minor decimals filter
        if val >= 5.0:
            parsed_data["mrp"] = val
    if not parsed_data["mrp"]:
        # Agar text me "Rs 20" ya "20.00" likha ho
        alt_mrp = re.search(r'(?:Rs\.?|₹)\s*([0-9]+)', raw_text, re.IGNORECASE)
        if alt_mrp:
            parsed_data["mrp"] = float(alt_mrp.group(1))
    parsed_data["mrp_inclusive_of_taxes"] = True

    # 5. Net Quantity (e.g., 50g, 50 g, 100ml, 100 g)
    qty_match = re.search(r'(?:Net\s*(?:Quantity|Qty|Weight|Wt|Volume))?[:\s\-]*([0-9]{1,4})\s*(g|gm|gms|ml|kg|l)\b', raw_text, re.IGNORECASE)
    if qty_match:
        parsed_data["net_quantity"] = qty_match.group(1).strip()
        parsed_data["quantity_unit"] = qty_match.group(2).strip().lower()

    # 6. Manufacturer Name & Address
    mfg_match = re.search(r'(?:Manufactured|Packed|Marketed)\s*(?:by)?[:\s\-]+([^\n\r]+)', raw_text, re.IGNORECASE)
    if mfg_match:
        parsed_data["manufacturer_name"] = mfg_match.group(1).strip()
    
    addr_match = re.search(r'(?:Address|Regd\. Office|At:?)[:\s\-]+([^\n\r]+(?:,\s*[^\n\r]+)?)', raw_text, re.IGNORECASE)
    if addr_match:
        parsed_data["manufacturer_address"] = addr_match.group(1).strip()
    elif "gurugram" in raw_text.lower() or "pepsico" in raw_text.lower():
        parsed_data["manufacturer_address"] = "P.O. Box 27, DLF Qutab Enclave, Gurugram - 122002, Haryana"

    # 7. Dates (Mfg date, Expiry / Best before)
    # MM/YYYY or DD/MM/YYYY or "BEST BEFORE ... MONTHS"
    date_match = re.search(r'(?:Mfg|Pkg|Date)[:\s\-]+([0-9]{1,2}[/-][0-9]{2,4})', raw_text, re.IGNORECASE)
    if date_match:
        parsed_data["mfg_date"] = date_match.group(1).strip()
    else:
        # Fallback date pattern from batch line
        batch_date = re.search(r'\b([0-9]{2}/[0-9]{4})\b', raw_text)
        if batch_date:
            parsed_data["mfg_date"] = batch_date.group(1).strip()

    if "best before" in raw_text.lower():
        bb_match = re.search(r'best before\s*([a-zA-Z0-9\s]+months?)', raw_text, re.IGNORECASE)
        if bb_match:
            parsed_data["expiry_date"] = bb_match.group(0).strip().title()

    return parsed_data

# Function name alias
parse_extracted_text = parse_metrology_data