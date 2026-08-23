import re
from utils.skills_db import SKILLS_DB, EXPERIENCE_KEYWORDS


def extract_skills(text: str):
    text_l = text.lower()
    found = []
    for skill in SKILLS_DB:
        if skill.lower() in text_l:
            found.append(skill)
    return found


def extract_experience_level(text: str):
    text_l = text.lower()
    for level, keywords in EXPERIENCE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_l:
                return level
    return "Intermediate"


def extract_budget(text: str):
    matches = re.findall(r"\$?\s?(\d{1,4})\s?(?:-|to)\s?\$?\s?(\d{1,4})", text)
    if matches:
        low, high = matches[0]
        return int(low), int(high)
    single = re.findall(r"\$\s?(\d{1,4})\s?(?:/hr|per hour|/hour)?", text)
    if single:
        v = int(single[0])
        return v, v
    return None


def read_uploaded_file(uploaded_file):
    """Best-effort text extraction from an uploaded JD/resume file."""
    name = uploaded_file.name.lower()
    raw = uploaded_file.read()
    if name.endswith(".txt"):
        return raw.decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(raw))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return "[Could not parse PDF in this environment — please paste the text instead.]"
    if name.endswith(".docx"):
        try:
            import docx
            import io
            d = docx.Document(io.BytesIO(raw))
            return "\n".join(p.text for p in d.paragraphs)
        except Exception:
            return "[Could not parse DOCX in this environment — please paste the text instead.]"
    return raw.decode("utf-8", errors="ignore")
