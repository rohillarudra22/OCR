import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "sih_2026_metrology_secret_token_9843")
    DATABASE_PATH = os.path.join(BASE_DIR, "metrology.db")
    SCHEMA_PATH = os.path.join(BASE_DIR, "database.sql")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    
    # Keras-OCR & preprocessing settings
    OCR_MAX_DIMENSION = 1600
    CUSTOM_WEIGHTS_PATH = os.path.join(BASE_DIR, "ml_engine", "weights", "recognizer_weights.h5")