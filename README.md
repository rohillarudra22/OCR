# OCR
Software System to check compliance of packaged commodities under legally metrology ( packaged commodities) rules, 2011 by scanning products, images and labels
# Legal Metrology Compliance Auditor (Packaged Commodities Rules, 2011)

An automated computer vision and statutory verification system designed for the Smart India Hackathon (SIH). The platform inspects front and back packaging labels to detect non-compliant or omitted declarations under the Legal Metrology (Packaged Commodities) Rules, 2011.

## Key Features
- **Dual-Side Image Inspection:** Accepts both front and back packaging panels via file upload or real-time webcam capture.
- **OCR Engine:** Extracts text using `keras-ocr` with custom contrast preprocessing via OpenCV.
- **Rule 6 Statutory Verification:**
  - Mandatory MRP declaration & "Inclusive of all taxes" syntax.
  - Standard SI metric units for Net Quantity (`g`, `kg`, `ml`, `l`).
  - Month and year of manufacture (with future post-dating detection).
  - Registered manufacturer / packer address and Country of Origin.
  - Mandatory consumer care telephone and email channels.
- **Audit History:** Stores all inspections and rule infraction logs in an SQL database.

## Quickstart Setup
```bash
git clone [https://github.com/your-username/legal-metrology-checker.git](https://github.com/your-username/legal-metrology-checker.git)
cd legal-metrology-checker

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

python app.py