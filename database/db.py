import os
import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "metrology.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.sql")
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users.csv")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def seed_users_from_excel(conn, file_path=CSV_PATH):
    """Reads users from CSV or Excel and seeds them into the database."""
    if not os.path.exists(file_path):
        print(f"Notice: '{file_path}' not found. Falling back to default user.")
        return False

    try:
        if file_path.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    # Normalize column names to lowercase and trim spaces
    df.columns = [str(col).strip().lower() for col in df.columns]

    # Find matching columns even if named 'user', 'username', 'password', 'pwd'
    user_col = next((c for c in df.columns if c in ["username", "user", "inspector", "inspector_id"]), None)
    pass_col = next((c for c in df.columns if c in ["password", "pass", "pwd"]), None)

    if not user_col or not pass_col:
        print(f"Error: CSV must contain 'username' and 'password' headers. Found: {list(df.columns)}")
        return False

    cursor = conn.cursor()
    imported_count = 0

    for _, row in df.iterrows():
        if pd.isna(row[user_col]) or pd.isna(row[pass_col]):
            continue

        username = str(row[user_col]).strip()
        raw_password = str(row[pass_col]).strip()

        if not username or not raw_password:
            continue

        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            hashed_pw = generate_password_hash(raw_password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed_pw)
            )
            imported_count += 1

    conn.commit()
    if imported_count > 0:
        print(f"✓ Imported {imported_count} users from {os.path.basename(file_path)}.")
    return True

def init_db():
    conn = get_db_connection()
    
    # 1. Initialize tables from database.sql
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())

    # 2. Seed from users.csv if present
    seeded = seed_users_from_excel(conn)

    # 3. Fallback: Always ensure at least 'rudra' exists if no CSV is found
    if not seeded:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", ("rudra",))
        if not cursor.fetchone():
            hashed_pw = generate_password_hash("password")
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("rudra", hashed_pw))
            conn.commit()

    conn.close()

def save_scan_record(user_id, category, front_path, back_path, raw_text, parsed_json_str, is_compliant, violations_str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_scans 
        (user_id, category, front_image_path, back_image_path, extracted_text, parsed_json, is_compliant, violations)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, category, front_path, back_path, raw_text, parsed_json_str, is_compliant, violations_str))
    conn.commit()
    scan_id = cursor.lastrowid
    conn.close()
    return scan_id