"""
Smart Recruitment Assistant - Document Parser Utility
---------------------------------------------------

Description:
Provides a unified function to extract text and metadata from various document formats 
(PDF, DOCX, TXT, HTML).

Dependencies:
    - pdfplumber
    - PyMuPDF (fitz)
    - pytesseract
    - pillow
    - docx2txt
    - langdetect
    - bs4
"""

import os
import fitz
import pdfplumber
import pytesseract
import docx2txt
import logging
from PIL import Image
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory

# -------------------- CONFIGURATION -------------------- #
OCR_DPI = 250  # Default OCR resolution
DetectorFactory.seed = 0

# -------------------- HELPER FUNCTIONS -------------------- #
def _detect_language(text: str) -> str:
    """Detect language of a given text."""
    try:
        if len(text) < 30:
            return "unknown"
        return detect(text)
    except Exception:
        return "unknown"


def _quality_score(text: str) -> float:
    """Compute a basic text quality score."""
    if not text:
        return 0.0
    alpha_ratio = sum(c.isalpha() for c in text) / len(text)
    word_ratio = len(text.split()) / 100
    return round(alpha_ratio * word_ratio, 2)


def _extract_from_pdf(pdf_path: str) -> tuple[str, str]:
    """Extract text from PDF using pdfplumber with OCR fallback."""
    text = []
    method = "pdfplumber"
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text.append(t)
        
        extracted_text = "\n".join(text).strip()
        
        # Fallback to OCR if text is too short
        if len(extracted_text) < 100:
            method = "ocr"
            text = []
            doc = fitz.open(pdf_path)
            for i, page in enumerate(doc):
                pix = page.get_pixmap(dpi=OCR_DPI)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ocr_text = pytesseract.image_to_string(img)
                text.append(ocr_text)
            extracted_text = "\n".join(text).strip()
            
        return extracted_text, method
    except Exception as e:
        logging.error(f"[PDF] Error for {pdf_path}: {e}")
        return "", method


def _extract_from_docx(docx_path: str) -> str:
    """Extract text from DOCX."""
    try:
        raw = docx2txt.process(docx_path)
        lines = [line.replace("\t", " ") for line in raw.split("\n") if line.strip()]
        return "\n".join(lines)
    except Exception as e:
        logging.error(f"[docx2txt] Error for {docx_path}: {e}")
        return ""


def _extract_from_txt(txt_path: str) -> str:
    """Extract text from TXT."""
    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        logging.error(f"[TXT] Error for {txt_path}: {e}")
        return ""


def _extract_from_html(html_path: str) -> str:
    """Extract text from HTML."""
    try:
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")
        return soup.get_text(separator="\n")
    except Exception as e:
        logging.error(f"[HTML] Error for {html_path}: {e}")
        return ""


# -------------------- MAIN INTERFACE -------------------- #
def extract_text(file_path: str) -> dict:
    """
    Extracts text and metadata from a document based on its file extension.

    Args:
        file_path (str): Absolute path to the file to be parsed.

    Returns:
        dict: A dictionary containing:
            - text (str): The extracted text.
            - meta (dict): Metadata about the extraction (method, language, stats).
            Returns None if file format is unsupported or extraction fails.
    """
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return None

    base = os.path.basename(file_path)
    _, ext = os.path.splitext(base)
    ext = ext.lower()
    
    method = ""
    text = ""

    if ext == ".pdf":
        text, method = _extract_from_pdf(file_path)
    elif ext == ".docx":
        text = _extract_from_docx(file_path)
        method = "docx2txt"
    elif ext == ".txt":
        text = _extract_from_txt(file_path)
        method = "plain_text"
    elif ext == ".html":
        text = _extract_from_html(file_path)
        method = "html_parser"
    else:
        logging.warning(f"Unsupported file format: {file_path}")
        return None

    # Metadata computation
    chars = len(text)
    words = len(text.split())
    lang = _detect_language(text)
    q_score = _quality_score(text)

    return {
        "text": text,
        "meta": {
            "filename": base,
            "method": method,
            "language": lang,
            "chars": chars,
            "words": words,
            "quality_score": q_score
        }
    }
