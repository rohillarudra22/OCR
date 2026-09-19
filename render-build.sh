#!/usr/bin/env bash
set -o errexit

# Linux container mein Tesseract OCR install karne ke liye
apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-hin libgl1

# Python packages install karein
pip install -r requirements.txt