import os
from typing import List
from pypdf import PdfReader
import docx

def extract_text_from_file(file_path: str) -> str:
    """
    Extracts text from a file, supporting PDF and DOCX formats.

    Args:
        file_path: The path to the file.

    Returns:
        The extracted text.
    """
    _, file_extension = os.path.splitext(file_path)
    text = ""
    if file_extension.lower() == ".pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text()
    elif file_extension.lower() == ".docx":
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        # For other file types, you might want to add more parsers
        # or just read them as plain text.
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    return text
