"""
Smart Recruitment Assistant - Phase 2 (Improved, No Config)
------------------------------------------------------------
Advanced Text Extraction Pipeline (v2)
Author: <Your Name>
Role: Person 1 - Data Pipeline & Preprocessing
Date: 2025-11-05

Description:
Extracts text from CVs and job offers (PDF, DOCX, TXT, HTML),
with OCR fallback, language detection, and structured JSON output.

Dependencies:
    - pdfplumber
    - PyMuPDF (fitz)
    - pytesseract
    - pillow
    - docx2txt
    - langdetect
    - bs4
    - pandas
    - tqdm
"""

import os
import fitz
import pdfplumber
import pytesseract
import docx2txt
import pandas as pd
import logging
import json
from PIL import Image
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime
from langdetect import detect, DetectorFactory

# -------------------- CONFIGURATION -------------------- #
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "..", "data", "cvs")        # dossier des CVs
OUT_DIR = os.path.join(ROOT_DIR, "..", "output", "raw_text")  # sortie texte
LOG_DIR = os.path.join(ROOT_DIR, "..", "output", "logs")      # logs
MANIFEST_PATH = os.path.join(LOG_DIR, "extraction_manifest.csv")
OCR_DPI = 250  # résolution OCR

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Optional: spécifie le chemin de Tesseract sur Windows si besoin
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -------------------- LOGGING SETUP -------------------- #
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "extraction.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logging.info("=== Starting Extraction Pipeline v2 ===")

DetectorFactory.seed = 0

# -------------------- UTIL FUNCTIONS -------------------- #
def detect_language(text: str) -> str:
    """Detect language of a given text."""
    try:
        if len(text) < 30:
            return "unknown"
        return detect(text)
    except Exception:
        return "unknown"


def quality_score(text: str) -> float:
    """Compute a basic text quality score."""
    if not text:
        return 0.0
    alpha_ratio = sum(c.isalpha() for c in text) / len(text)
    word_ratio = len(text.split()) / 100
    return round(alpha_ratio * word_ratio, 2)


def save_text(text: str, out_path: str):
    """Save extracted text to .txt"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)


def save_json(text: str, out_path: str, meta: dict):
    """Save structured JSON output"""
    data = {"text": text, "meta": meta}
    with open(out_path.replace(".txt", ".json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------- EXTRACTION METHODS -------------------- #
def extract_text_pdfplumber(pdf_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text.append(t)
    except Exception as e:
        logging.error(f"[pdfplumber] Error for {pdf_path}: {e}")
    return "\n".join(text).strip()


def extract_text_ocr_pymupdf(pdf_path: str, dpi=200) -> str:
    """OCR extraction for scanned PDFs."""
    text = []
    try:
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=dpi)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img)
            text.append(ocr_text)
    except Exception as e:
        logging.error(f"[OCR] Error for {pdf_path}: {e}")
    return "\n".join(text).strip()


def extract_text_docx(docx_path: str) -> str:
    """Extract text from DOCX."""
    try:
        raw = docx2txt.process(docx_path)
        lines = [line.replace("\t", " ") for line in raw.split("\n") if line.strip()]
        return "\n".join(lines)
    except Exception as e:
        logging.error(f"[docx2txt] Error for {docx_path}: {e}")
        return ""


def extract_text_txt(txt_path: str) -> str:
    """Extract text from TXT."""
    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        logging.error(f"[TXT] Error for {txt_path}: {e}")
        return ""


def extract_text_html(html_path: str) -> str:
    """Extract text from HTML."""
    try:
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")
        return soup.get_text(separator="\n")
    except Exception as e:
        logging.error(f"[HTML] Error for {html_path}: {e}")
        return ""

# -------------------- MAIN PIPELINE -------------------- #
def extract_all():
    """Main controller for text extraction from all supported files."""

    results = []
    all_files = [
        os.path.join(DATA_DIR, f)
        for f in os.listdir(DATA_DIR)
        if f.lower().endswith((".pdf", ".docx", ".txt", ".html"))
    ]

    if not all_files:
        print("❌ Aucun fichier trouvé dans data/cvs/")
        return

    print(f"🚀 Starting extraction for {len(all_files)} documents...\n")

    for file in tqdm(all_files, desc="Extracting"):
        base = os.path.basename(file)
        name, ext = os.path.splitext(base)
        out_path = os.path.join(OUT_DIR, f"{name}.txt")
        method = ""
        text = ""

        # Extraction routing
        if ext.lower() == ".pdf":
            text = extract_text_pdfplumber(file)
            method = "pdfplumber"
            if len(text) < 100:
                text = extract_text_ocr_pymupdf(file, dpi=OCR_DPI)
                method = "ocr"
        elif ext.lower() == ".docx":
            text = extract_text_docx(file)
            method = "docx2txt"
        elif ext.lower() == ".txt":
            text = extract_text_txt(file)
            method = "plain_text"
        elif ext.lower() == ".html":
            text = extract_text_html(file)
            method = "html_parser"
        else:
            logging.warning(f"Unsupported file format: {file}")
            continue

        # Metadata
        chars = len(text)
        words = len(text.split())
        lang = detect_language(text)
        q_score = quality_score(text)

        meta = {
            "filename": base,
            "method": method,
            "language": lang,
            "chars": chars,
            "words": words,
            "quality_score": q_score,
            "timestamp": datetime.now().isoformat(),
        }

        # Save results
        save_text(text, out_path)
        save_json(text, out_path, meta)

        results.append(meta)
        logging.info(f"✅ Extracted {base} ({method}) - Lang:{lang}, Score:{q_score}")

    # Save manifest
    pd.DataFrame(results).to_csv(MANIFEST_PATH, index=False)
    print(f"\n✅ Extraction terminée !\n📁 Output: {OUT_DIR}\n📄 Manifest: {MANIFEST_PATH}")


# -------------------- ENTRY POINT -------------------- #
if __name__ == "__main__":
    extract_all()
