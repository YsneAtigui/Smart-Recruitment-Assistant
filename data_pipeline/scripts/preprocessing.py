"""
Smart Recruitment Assistant - (Final JSON Output)
----------------------------------------------------------
Preprocess resumes into a structured JSON format:
- raw_text (from extraction)
- cleaned_light (entity-safe)
- cleaned_semantic (normalized for embeddings)
- metadata and stats for QA

"""

import os
import re
import json
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from unidecode import unidecode

# -------------------- CONFIG -------------------- #
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(ROOT_DIR, "..", "output", "raw_text")
OUT_DIR = os.path.join(ROOT_DIR, "..", "output", "processed")
LOG_DIR = os.path.join(ROOT_DIR, "..", "output", "logs")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

OUT_JSON = os.path.join(OUT_DIR, "preprocessed_resumes.json")
MANIFEST_PATH = os.path.join(LOG_DIR, "cleaning_manifest.jsonl")

# -------------------- CLEANING FUNCTIONS -------------------- #

def clean_light(text: str) -> str:
    """Preserve structure, entities, and readability for extraction."""
    if not text:
        return ""

    text = unidecode(text)

    # Protect entities
    emails = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    for i, e in enumerate(emails):
        text = text.replace(e, f"__EMAIL_{i}__")

    urls = re.findall(r"(?:https?://\S+|www\.\S+)", text)
    for i, u in enumerate(urls):
        text = text.replace(u, f"__URL_{i}__")

    phones = re.findall(r"\+?\d[\d\s\-\(\)]{6,}\d", text)
    for i, p in enumerate(phones):
        text = text.replace(p, f"__PHONE_{i}__")

    # Clean text but preserve structure
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    text = re.sub(r"[•·●]", "-", text)
    text = re.sub(r"(?<=\w),(?=\w)", ", ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)

    # Restore entities
    for i, e in enumerate(emails):
        text = text.replace(f"__EMAIL_{i}__", e)
    for i, u in enumerate(urls):
        text = text.replace(f"__URL_{i}__", u)
    for i, p in enumerate(phones):
        text = text.replace(f"__PHONE_{i}__", p)

    # Line structure normalization
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    text = "\n".join(lines)

    # Fix merged words and spacing
    text = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", text)
    text = re.sub(r"(\d)([A-Za-z])", r"\1 \2", text)

    return text.strip()


def clean_semantic(text: str) -> str:
    """Light normalization for embeddings & semantic scoring."""
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^a-z0-9@\+\#\-\._:/\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------- MAIN PIPELINE -------------------- #

def preprocess_all_to_json():
    files = [f for f in os.listdir(RAW_DIR) if f.endswith(".txt")]
    if not files:
        print("❌ No text files found in output/raw_text/")
        return

    print(f"🧠 Starting preprocessing for {len(files)} resumes...\n")

    all_resumes = []
    manifest = []

    for fname in tqdm(files, desc="Processing"):
        in_path = os.path.join(RAW_DIR, fname)
        candidate_id = os.path.splitext(fname)[0]

        try:
            with open(in_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            cleaned_light = clean_light(raw_text)
            cleaned_semantic = clean_semantic(cleaned_light)

            # Compute basic stats
            stats = {
                "chars": len(raw_text),
                "words": len(raw_text.split()),
                "lines": len(raw_text.splitlines())
            }

            resume_record = {
                "id": candidate_id,
                "language": "en",
                "raw_text": raw_text,
                "cleaned_light": cleaned_light,
                "cleaned_semantic": cleaned_semantic,
                "meta": {
                    "method": "pdfplumber",
                    "stats": stats,
                    "quality_score": round((stats["words"] / (stats["lines"] + 1)), 2),
                    "timestamp": datetime.now().isoformat()
                }
            }

            all_resumes.append(resume_record)

            manifest.append({
                "filename": fname,
                "id": candidate_id,
                "chars": stats["chars"],
                "words": stats["words"],
                "lines": stats["lines"],
                "timestamp": resume_record["meta"]["timestamp"]
            })

        except Exception as e:
            print(f"⚠️ Error processing {fname}: {e}")

    # Save combined JSON
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_resumes, f, indent=2, ensure_ascii=False)

    # Save manifest log
    pd.DataFrame(manifest).to_json(MANIFEST_PATH, orient="records", indent=2)

    print(f"\n✅ Preprocessing completed successfully!")
    print(f"📘 Output JSON: {OUT_JSON}")
    print(f"🧾 Manifest: {MANIFEST_PATH}")
    print(f"📂 Total resumes processed: {len(all_resumes)}")


# -------------------- ENTRY POINT -------------------- #
if __name__ == "__main__":
    preprocess_all_to_json()
