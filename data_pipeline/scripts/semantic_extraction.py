"""
Smart Recruitment Assistant - Semantic Extraction
----------------------------------------------------------
Reads:  output/processed/preprocessed_resumes.json
Writes: output/structured_data/semantic_extracted.json
        output/structured_data/semantic_manifest.csv

Description:
Extracts structured candidate information (name, contact, skills, education, experience)
using spaCy NER + regex + rule-based parsing.
"""

import os
import re
import json
import pandas as pd
from datetime import datetime
from collections import defaultdict
from tqdm import tqdm
from dateutil import parser as dateparser, relativedelta
import spacy

# ------------------ PATH CONFIG ------------------ #
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IN_JSON = os.path.join(ROOT_DIR, "..", "output", "processed", "preprocessed_resumes.json")
OUT_DIR = os.path.join(ROOT_DIR, "..", "output", "structured_data")
SKILLS_CSV = os.path.join(ROOT_DIR, "..", "data", "skills.csv")

os.makedirs(OUT_DIR, exist_ok=True)
OUT_JSON = os.path.join(OUT_DIR, "semantic_extracted.json")
OUT_CSV = os.path.join(OUT_DIR, "semantic_manifest.csv")

# ------------------ LOAD MODELS ------------------ #
print("➡️ Loading spaCy model (en_core_web_sm)...")
try:
    nlp = spacy.load("en_core_web_sm")
    print("✅ Loaded en_core_web_sm successfully.")
except Exception as e:
    raise RuntimeError("❌ Could not load spaCy English model. Run: python -m spacy download en_core_web_sm") from e

# ------------------ LOAD SKILLS ------------------ #
def load_skills(path):
    if not os.path.exists(path):
        print(f"⚠️ skills.csv not found at {path}. Using fallback list.")
        return {"python", "java", "sql", "nlp", "django", "flask", "html", "css", "javascript"}
    try:
        df = pd.read_csv(path, header=None, dtype=str)
        skills = set(df.stack().dropna().str.lower().str.strip())
        return skills
    except Exception as e:
        print("⚠️ Error loading skills.csv:", e)
        return set()

SKILL_SET = load_skills(SKILLS_CSV)
print(f"✅ Loaded {len(SKILL_SET)} skills from CSV.")

# ------------------ REGEX HELPERS ------------------ #
EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_RE = re.compile(r"\+?\d[\d\s\-\(\)]{6,}\d")
URL_RE = re.compile(r"(https?://\S+|www\.\S+)")
RANGE_RE = re.compile(r"(?P<start>[^,\n\r]+?)\s*(?:-|–|—|to|until|through)\s*(?P<end>[^,\n\r]+)", re.I)

# ------------------ SECTION SPLITTING ------------------ #
SECTION_KEYWORDS = {
    "experience": ["experience", "work history", "employment"],
    "education": ["education", "academic", "qualification"],
    "skills": ["skills", "technical skills", "competencies"],
    "projects": ["projects", "personal projects"],
    "certifications": ["certifications", "certificates"],
    "honors": ["honors", "awards"],
    "activities": ["activities", "volunteering"]
}

def find_section_for_line(line):
    line_l = line.lower()
    for section, variants in SECTION_KEYWORDS.items():
        if any(v in line_l for v in variants):
            return section
    return None

def split_sections(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    sections = defaultdict(list)
    current = "general"
    for ln in lines:
        sec = find_section_for_line(ln)
        if sec:
            current = sec
        else:
            sections[current].append(ln)
    return {k: "\n".join(v).strip() for k, v in sections.items() if v}

# ------------------ INFO EXTRACTION ------------------ #
def extract_contacts(text):
    email = next(iter(EMAIL_RE.findall(text)), None)
    phone = next(iter(PHONE_RE.findall(text)), None)
    links = URL_RE.findall(text)
    return email, phone, links

def extract_skills_from_text(text):
    text_l = text.lower()
    found = {s for s in SKILL_SET if s in text_l}
    return sorted(found)

def parse_date_safe(date_str):
    s = re.sub(r"[–—,·•]", " ", date_str).strip()
    try:
        return dateparser.parse(s, default=datetime(2000, 1, 1))
    except Exception:
        y = re.search(r"(\d{4})", s)
        if y:
            return datetime(int(y.group(1)), 1, 1)
    return None

def extract_experience_items(section_text):
    if not section_text:
        return []
    lines = [l for l in section_text.splitlines() if l.strip()]
    items, chunk = [], []
    for l in lines:
        if re.search(r"\d{4}", l) or re.match(r"^\s*[-•\*]\s+", l):
            if chunk:
                items.append(" ".join(chunk))
                chunk = [l]
            else:
                chunk = [l]
        else:
            chunk.append(l)
    if chunk:
        items.append(" ".join(chunk))

    parsed_items = []
    for raw in items:
        start = end = None
        rmatch = RANGE_RE.search(raw)
        if rmatch:
            s_text = rmatch.group("start").strip()
            e_text = rmatch.group("end").strip()
            start_dt = parse_date_safe(s_text)
            end_dt = None if re.search(r"present|current", e_text, re.I) else parse_date_safe(e_text)
        else:
            dates = re.findall(r"([A-Za-z]{3,9}\s*\d{4}|\d{4})", raw)
            start_dt = parse_date_safe(dates[0]) if dates else None
            end_dt = parse_date_safe(dates[1]) if len(dates) > 1 else None
        parsed_items.append({
            "raw": raw,
            "start_dt": start_dt.isoformat() if start_dt else None,
            "end_dt": end_dt.isoformat() if end_dt else None,
            "duration_months": None
        })
    return parsed_items

def compute_total_experience_months(items):
    total = 0
    for it in items:
        if it["start_dt"]:
            sdt = dateparser.parse(it["start_dt"])
            edt = dateparser.parse(it["end_dt"]) if it["end_dt"] else datetime.now()
            diff = relativedelta.relativedelta(edt, sdt)
            total += diff.years * 12 + diff.months
    return total

# ------------------ MAIN PROCESS ------------------ #
def semantic_extraction_pipeline(in_json_path=IN_JSON):
    if not os.path.exists(in_json_path):
        raise FileNotFoundError(f"❌ Input file not found: {in_json_path}")
    with open(in_json_path, "r", encoding="utf-8") as f:
        resumes = json.load(f)

    results, manifest = [], []

    for r in tqdm(resumes, desc="Semantic extraction"):
        text = r.get("cleaned_light") or r.get("raw_text") or ""
        candidate_id = r.get("id", f"candidate_{len(results)+1}")

        sections = split_sections(text)
        email, phone, links = extract_contacts(text)
        doc = nlp(text)
        name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), None)
        skills = extract_skills_from_text(sections.get("skills", text))
        edu_lines = [ln for ln in sections.get("education", "").splitlines() if re.search(r"(degree|bachelor|master|phd|college|university|\d{4})", ln, re.I)]
        exp_items = extract_experience_items(sections.get("experience", ""))
        total_months = compute_total_experience_months(exp_items)
        total_years = round(total_months / 12, 2) if total_months else None

        record = {
            "candidate_id": candidate_id,
            "name": name,
            "email": email,
            "phone": phone,
            "links": links,
            "skills": skills,
            "education": edu_lines,
            "experience": {"items": exp_items, "total_months": total_months, "total_years": total_years},
            "sections": sections,
            "created_at": datetime.now().isoformat()
        }
        results.append(record)
        manifest.append({
            "candidate_id": candidate_id,
            "name": name,
            "email": email,
            "phone": phone,
            "skills_count": len(skills),
            "education_count": len(edu_lines),
            "exp_items": len(exp_items),
            "total_years": total_years
        })

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    pd.DataFrame(manifest).to_csv(OUT_CSV, index=False)
    print(f"\n✅ Semantic extraction complete.\n📄 JSON: {OUT_JSON}\n📊 CSV: {OUT_CSV}\nCount: {len(results)}")

if __name__ == "__main__":
    semantic_extraction_pipeline()
