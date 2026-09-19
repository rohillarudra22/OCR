import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

from database.db import get_db_connection, init_db, save_scan_record
from ml_engine.ocr_pipeline import extract_text_from_images
from ml_engine.parser import parse_extracted_text
from rules_engine.validator import LegalMetrologyValidator

app = Flask(__name__)
app.secret_key = "sih_hackathon_super_secret_key"
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database schema on startup
with app.app_context():
    init_db()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Incorrect username or password. Please try again.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access the verification portal.", "warning")
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/process-scan", methods=["POST"])
def process_scan():
    if "user_id" not in session:
        return redirect(url_for("login"))

    category = request.form.get("category")
    front_file = request.files.get("front_image")
    back_file = request.files.get("back_image")

    if not category or not front_file or not back_file or front_file.filename == "" or back_file.filename == "":
        flash("Category, front image, and back image are all required.", "error")
        return redirect(url_for("dashboard"))

    if not (allowed_file(front_file.filename) and allowed_file(back_file.filename)):
        flash("Invalid file format. Upload PNG, JPG, or JPEG.", "error")
        return redirect(url_for("dashboard"))

    # Save images securely
    front_filename = secure_filename(f"front_{front_file.filename}")
    back_filename = secure_filename(f"back_{back_file.filename}")
    front_path = os.path.join(app.config["UPLOAD_FOLDER"], front_filename)
    back_path = os.path.join(app.config["UPLOAD_FOLDER"], back_filename)

    front_file.save(front_path)
    back_file.save(back_path)

    # 1. Extract text using OCR pipeline
    raw_ocr_text = extract_text_from_images(front_path, back_path)

    # 2. Parse extracted text
    parsed_data = parse_extracted_text(raw_ocr_text)

    # 3. Validate against Legal Metrology Rules
    validator = LegalMetrologyValidator(parsed_data, category)
    validation_result = validator.evaluate()

    # 4. Save audit log into DB
    scan_id = save_scan_record(session["user_id"], category, f"uploads/{front_filename}", f"uploads/{back_filename}", raw_ocr_text, json.dumps(parsed_data), validation_result["compliant"], json.dumps(validation_result["violations"]))

    session["scan_id"] = scan_id
    return redirect(url_for("result_view", scan_id=scan_id))

@app.route("/result/<int:scan_id>")
def result_view(scan_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    scan = conn.execute(
        "SELECT * FROM audit_scans WHERE id = ? AND user_id = ?",
        (scan_id, session["user_id"])
    ).fetchone()
    conn.close()

    if not scan:
        flash("Scan record not found.", "warning")
        return redirect(url_for("dashboard"))

    # Gracefully handle column names if parsed_json or validation_errors is stored
    parsed_data = json.loads(scan["parsed_json"]) if "parsed_json" in scan.keys() and scan["parsed_json"] else {}
    violations = json.loads(scan["validation_errors"]) if "validation_errors" in scan.keys() and scan["validation_errors"] else (
        json.loads(scan["violations"]) if "violations" in scan.keys() and scan["violations"] else []
    )

    return render_template(
        "result.html",
        scan=scan,
        parsed_data=parsed_data,
        violations=violations
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)