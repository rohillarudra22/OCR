import os
import sys
import json

# Ensure project modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_engine.ocr_pipeline import extract_text_from_images
from ml_engine.parser import parse_extracted_text
from rules_engine.validator import LegalMetrologyValidator

def run_test(front_image_path: str, back_image_path: str, category: str = "Food & Beverages"):
    print("=" * 60)
    print("STEP 1: Verifying image files exist...")
    if not os.path.exists(front_image_path):
        print(f"ERROR: Front image not found at '{front_image_path}'")
        return
    if not os.path.exists(back_image_path):
        print(f"ERROR: Back image not found at '{back_image_path}'")
        return
    print("✓ Image files located successfully.\n")

    print("=" * 60)
    print("STEP 2: Running OCR Extraction Pipeline...")
    print("(Note: On first run, model weights will download automatically)")
    try:
        raw_ocr_text = extract_text_from_images([front_image_path, back_image_path])
        print("✓ Raw text extracted successfully!")
        print("-" * 40)
        print("RAW DETECTED TEXT PREVIEW:")
        print(raw_ocr_text[:300] + ("..." if len(raw_ocr_text) > 300 else ""))
        print("-" * 40 + "\n")
    except Exception as e:
        print(f"ERROR during OCR execution: {e}")
        return

    print("=" * 60)
    print("STEP 3: Parsing Raw Text into Structured JSON...")
    parsed_json = parse_extracted_text(raw_ocr_text)
    print(json.dumps(parsed_json, indent=2))
    print("✓ JSON parsing complete.\n")

    print("=" * 60)
    print(f"STEP 4: Validating Under Legal Metrology Rules, 2011 (Category: {category})...")
    validator = LegalMetrologyValidator(parsed_json, category)
    result = validator.evaluate()

    print("\n--- COMPLIANCE SUMMARY REPORT ---")
    if result["compliant"]:
        print("STATUS: [PASS] Product adheres to Legal Metrology Rules.")
    else:
        print("STATUS: [FAIL] Product violates statutory labeling rules.")
        print(f"Total Violations: {result['violations_count']}")
        print("\nViolations List:")
        for idx, violation in enumerate(result["violations"], 1):
            print(f"  {idx}. {violation}")
    print("=" * 60)

if __name__ == "__main__":
    # Put two test images in your project root or static/uploads/
    # Replace these filenames with your actual sample image filenames:
    sample_front = "sample_front.jpg"
    sample_back = "sample_back.jpg"

    if len(sys.argv) == 3:
        sample_front = sys.argv[1]
        sample_back = sys.argv[2]

    run_test(sample_front, sample_back)