"""
Rule-based CV parser used by the "Upload CV" option on the profile page.

It reads plain text (already extracted from a PDF / DOCX / TXT by the caller)
and pulls out what it can recognise: name, title/headline, bio/summary,
skills and an experience level. It is deliberately simple and predictable —
regular expressions, section headings and a skills vocabulary, no machine
learning and no network calls — so results are always shown to the user as a
draft to review before anything is saved.

Only fields that were actually detected are returned, so a missed field never
overwrites what the user already has.
"""
import datetime
import re

EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Expert"]
MAX_SKILLS = 40

# --------------------------------------------------------------------------
# Section headings
# --------------------------------------------------------------------------
_SECTION_HEADINGS = {
    "summary": [
        "summary", "professional summary", "career summary", "profile",
        "professional profile", "personal profile", "about", "about me",
        "objective", "career objective", "professional objective",
        "personal statement", "overview",
    ],
    "skills": [
        "skills", "technical skills", "key skills", "core skills",
        "core competencies", "competencies", "technologies",
        "technical proficiencies", "tech stack", "tools",
        "tools & technologies", "tools and technologies", "skills & tools",
        "skills and tools", "skills & technologies", "areas of expertise",
        "expertise", "technical expertise", "skills summary",
        "professional skills",
    ],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment", "employment history", "work history", "career history",
        "internships", "internship experience", "relevant experience",
    ],
    # Headings we recognise only so they END the previous section.
    "other": [
        "education", "academic background", "qualifications",
        "academic qualifications", "projects", "academic projects",
        "personal projects", "certifications", "certificates",
        "licenses & certifications", "achievements", "accomplishments",
        "awards", "honors", "languages", "interests", "hobbies",
        "hobbies & interests", "references", "publications", "courses",
        "training", "volunteering", "volunteer experience",
        "personal details", "personal information", "contact",
        "contact information", "declaration", "activities",
        "extracurricular activities",
    ],
}
_HEADING_TO_SECTION = {
    heading: section
    for section, headings in _SECTION_HEADINGS.items()
    for heading in headings
}
_INLINE_HEADING = re.compile(r"^\s*([A-Za-z][A-Za-z &/]{1,40}?)\s*:\s*(\S.*)$")
_MAX_SKILL_SECTION_LINES = 25


def _normalize_heading(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z& ]+", " ", text.lower())).strip()


# --------------------------------------------------------------------------
# Skills vocabulary
# --------------------------------------------------------------------------
_SKILL_VOCAB = [
    # Languages
    "Python", "R", "SQL", "Java", "JavaScript", "TypeScript", "C", "C++", "C#",
    "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin", "Scala", "MATLAB", "Bash",
    "Shell Scripting", "PowerShell", "Dart", "Perl", "VBA", "SAS", "SPSS",
    "Julia",
    # Web / app development
    "HTML", "CSS", "React", "Angular", "Vue", "Next.js", "Node.js",
    "Express.js", "Django", "Flask", "FastAPI", "Spring Boot", "Laravel",
    "WordPress", "Bootstrap", "Tailwind CSS", "jQuery", ".NET", "ASP.NET",
    "REST API", "GraphQL", "Android", "iOS", "Flutter", "React Native",
    # Data science / ML / AI
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "Data Science", "Data Analysis", "Data Analytics", "Data Visualization",
    "Data Engineering", "Data Mining", "Data Cleaning", "Data Modeling",
    "Statistics", "Statistical Analysis", "Predictive Modeling",
    "Time Series", "Feature Engineering", "A/B Testing", "Regression",
    "Classification", "Clustering", "Reinforcement Learning",
    "Generative AI", "LLM", "Prompt Engineering", "RAG", "Hugging Face",
    "LangChain", "OpenAI", "Pandas", "NumPy", "SciPy", "Scikit-learn",
    "TensorFlow", "PyTorch", "Keras", "XGBoost", "LightGBM", "OpenCV",
    "NLTK", "spaCy", "Matplotlib", "Seaborn", "Plotly", "Streamlit",
    "Jupyter",
    # BI / analytics
    "Power BI", "Tableau", "Excel", "Looker", "Google Analytics", "DAX",
    "Power Query", "Google Sheets", "Qlik",
    # Databases / big data
    "MySQL", "PostgreSQL", "SQL Server", "SQLite", "Oracle", "MongoDB",
    "Redis", "Cassandra", "DynamoDB", "Firebase", "Snowflake", "BigQuery",
    "Redshift", "Databricks", "Spark", "PySpark", "Hadoop", "Hive", "Airflow",
    "Kafka", "dbt", "ETL", "Data Warehousing", "NoSQL",
    # Cloud / DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Jenkins",
    "GitHub Actions", "CI/CD", "Git", "GitHub", "GitLab", "Linux", "Ansible",
    "DevOps", "Microservices",
    # Testing / QA
    "Selenium", "Pytest", "JUnit", "Postman", "Cypress", "Unit Testing",
    "Manual Testing", "Test Automation",
    # Design / creative
    "Figma", "Adobe XD", "Photoshop", "Illustrator", "Canva", "UI/UX",
    "Wireframing", "Prototyping", "Video Editing", "Premiere Pro",
    "After Effects",
    # Marketing / content
    "SEO", "SEM", "Content Writing", "Copywriting", "Social Media Marketing",
    "Email Marketing", "Google Ads", "Content Strategy", "Technical Writing",
    "Blogging",
    # Business / management
    "Project Management", "Product Management", "Agile", "Scrum", "Jira",
    "Business Analysis", "Stakeholder Management", "Salesforce", "SAP",
    "Financial Modeling", "Accounting", "Tally", "QuickBooks",
    "Customer Support",
    # Other
    "Blockchain", "Solidity", "Unity", "Unreal Engine", "Arduino", "IoT",
    "Embedded Systems", "AutoCAD", "SolidWorks",
]
# Matched with exact capitalisation because the lowercase form is also an
# ordinary English word or a common name ("excel", "spark", "sap", "rag" ...).
_CASE_SENSITIVE = {
    "Excel", "Spark", "Swift", "Ruby", "Rust", "Bash", "SAP", "SAS", "RAG",
    "DAX", "SEM", "R", "C", "Go", "Julia", "Dart", "Unity",
}
# Too ambiguous to find by scanning running text ("R", "C", "Go" ...). They
# are only accepted when listed in the CV's Skills section.
_SECTION_ONLY = {"R", "C", "Go", "Julia", "Dart", "Unity"}

_VOCAB_LOOKUP = {skill.lower(): skill for skill in _SKILL_VOCAB}
_ALIASES = {
    "sklearn": "Scikit-learn", "scikit learn": "Scikit-learn",
    "powerbi": "Power BI", "power-bi": "Power BI", "ms power bi": "Power BI",
    "ms excel": "Excel", "microsoft excel": "Excel", "advanced excel": "Excel",
    "js": "JavaScript", "ts": "TypeScript", "ml": "Machine Learning",
    "dl": "Deep Learning", "postgres": "PostgreSQL", "k8s": "Kubernetes",
    "node": "Node.js", "nodejs": "Node.js", "reactjs": "React",
    "react.js": "React", "vuejs": "Vue", "vue.js": "Vue",
    "tf": "TensorFlow", "genai": "Generative AI", "gen ai": "Generative AI",
    "ci cd": "CI/CD", "cicd": "CI/CD", "rest apis": "REST API",
    "restful api": "REST API", "restful apis": "REST API",
    "rest": "REST API", "tailwind": "Tailwind CSS", "expressjs": "Express.js",
    "express": "Express.js", "nextjs": "Next.js", "amazon web services": "AWS",
    "google cloud": "GCP", "google cloud platform": "GCP",
    "natural language processing": "NLP", "large language models": "LLM",
    "llms": "LLM", "ui ux": "UI/UX", "ux/ui": "UI/UX", "ui/ux design": "UI/UX",
    "power bi desktop": "Power BI", "ms sql server": "SQL Server",
    "microsoft sql server": "SQL Server", "mongo db": "MongoDB",
    "html5": "HTML", "css3": "CSS", "html/css": "HTML",
}


def _skill_pattern(skill):
    flags = 0 if skill in _CASE_SENSITIVE else re.IGNORECASE
    return re.compile(
        r"(?<![A-Za-z0-9+#.])" + re.escape(skill) + r"(?![A-Za-z0-9+#])", flags
    )


_VOCAB_PATTERNS = [
    (skill, _skill_pattern(skill))
    for skill in _SKILL_VOCAB
    if skill not in _SECTION_ONLY
]

_TOKEN_STOP = {
    "and", "or", "etc", "others", "other", "skills", "tools", "technologies",
    "languages", "frameworks", "libraries", "programming", "databases",
    "platforms", "advanced", "intermediate", "beginner", "expert", "basic",
    "proficient", "fluent", "native", "good", "excellent", "strong", "the",
    "a", "of", "in", "with", "using", "n/a", "na", "none",
}
_LEADING_DESCRIPTOR = re.compile(
    r"^(?:advanced|basic|intermediate|proficient in|proficiency in|"
    r"knowledge of|working knowledge of|experience (?:in|with)|"
    r"familiar with|familiarity with|hands[- ]on(?: experience)?(?: in| with)?|"
    r"strong|good|excellent)\s+",
    re.IGNORECASE,
)
_BULLET = re.compile(r"^[\s•●▪◦‣·\-\*–—>»■□✓✔➢➤●○]+")


def _canonical(token):
    key = token.lower()
    if key in _ALIASES:
        return _ALIASES[key]
    if key in _VOCAB_LOOKUP:
        return _VOCAB_LOOKUP[key]
    if token.islower():
        return " ".join(w[:1].upper() + w[1:] for w in token.split(" "))
    return token


def _clean_token(raw):
    token = re.sub(r"\s+", " ", raw.strip(" \t.-–—*•·:;\"'")).strip()
    if not token:
        return None
    stripped = _LEADING_DESCRIPTOR.sub("", token, count=1).strip()
    if stripped:
        token = stripped
    low = token.lower()
    if low in _TOKEN_STOP:
        return None
    if len(token) > 32 or len(token.split()) > 4:
        return None
    if not re.search(r"[A-Za-z]", token):
        return None
    if re.search(r"\d{4}", token):  # a year: almost certainly not a skill
        return None
    return _canonical(token)


def _skill_tokens(lines):
    tokens = []
    for line in lines:
        line = _BULLET.sub("", line)
        label = re.match(r"^([A-Za-z][A-Za-z &/+\-]{1,30}?)\s*:\s*(\S.*)$", line)
        if label and len(label.group(1).split()) <= 4:
            line = label.group(2)
        line = re.sub(r"[()\[\]{}]", ",", line)
        line = re.sub(r"\s[-–—]\s", ",", line)
        for part in re.split(r"[,;|•●▪◦·\t]+|\s{3,}", line):
            pieces = [part]
            if re.search(r"\s(?:and|&)\s", part):
                subs = re.split(r"\s+(?:and|&)\s+", part)
                if all(len(s.split()) <= 3 for s in subs):
                    pieces = subs
            for piece in pieces:
                cleaned = _clean_token(piece)
                if cleaned:
                    tokens.append(cleaned)
    return tokens


def _vocab_matches(text):
    hits = []
    for skill, pattern in _VOCAB_PATTERNS:
        match = pattern.search(text)
        if match:
            hits.append((match.start(), skill))
    hits.sort()
    return [skill for _, skill in hits]


def _dedupe(items):
    seen, out = set(), []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def merge_skills(new_skills, existing_skills):
    """New (CV) skills first, then any existing ones not already present."""
    return _dedupe(list(new_skills) + list(existing_skills))


# --------------------------------------------------------------------------
# Name / title
# --------------------------------------------------------------------------
_TITLE_WORDS = {
    "developer", "engineer", "scientist", "analyst", "designer", "manager",
    "consultant", "specialist", "architect", "writer", "editor", "marketer",
    "administrator", "programmer", "researcher", "accountant", "strategist",
    "coordinator", "director", "freelancer", "intern", "officer", "executive",
    "technician", "teacher", "lecturer", "professor", "student", "graduate",
    "trainee", "associate", "lead", "head", "founder", "assistant",
    "copywriter", "translator", "photographer", "animator", "illustrator",
    "tester", "devops", "statistician",
}
_TITLE_REGEX = re.compile(
    r"\b(?:" + "|".join(sorted((w.strip(".") for w in _TITLE_WORDS),
                               key=len, reverse=True)) + r")s?\b",
    re.IGNORECASE,
)
_SEGMENT_SPLIT = re.compile(r"\s*[|•·●▪]\s*")
_PHONE = re.compile(r"\+?\d[\d\s().\-]{7,}\d")


def _looks_like_contact(text):
    low = text.lower()
    return bool(
        "@" in text or "http" in low or "www." in low
        or "linkedin" in low or "github.com" in low or _PHONE.search(text)
    )


def _as_name(segment):
    seg = segment.strip().strip(",;:-–—").strip()
    if not seg or _looks_like_contact(seg) or re.search(r"\d", seg):
        return None
    low = seg.lower()
    if any(w in low for w in ("curriculum", "vitae", "resume", "résumé")):
        return None
    if low in ("cv", "profile", "contact"):
        return None
    if _HEADING_TO_SECTION.get(_normalize_heading(seg)):
        return None
    words = seg.split()
    if not 2 <= len(words) <= 4:
        return None
    for word in words:
        if not re.fullmatch(r"[^\W\d_](?:[^\W\d_]|[.'’\-])*", word):
            return None
    if any(w.lower().strip(".") in _TITLE_WORDS for w in words):
        return None
    if all(w.islower() for w in words):
        return None
    if seg.isupper():
        return " ".join(w.capitalize() for w in words)
    return seg


def _find_name(lines):
    for line in lines[:20]:
        labelled = re.match(r"^\s*(?:full\s+)?name\s*[:\-–]\s*(.+)$", line, re.IGNORECASE)
        if labelled:
            name = _as_name(labelled.group(1))
            if name:
                return name, None
    for idx, line in enumerate(lines[:12]):
        for segment in _SEGMENT_SPLIT.split(line):
            name = _as_name(segment)
            if name:
                return name, idx
    return None, None


def _is_title_segment(segment):
    if not 3 <= len(segment) <= 90 or len(segment.split()) > 9:
        return False
    if _looks_like_contact(segment) or re.search(r"\d{4}", segment):
        return False
    if segment.rstrip().endswith("."):
        return False
    return bool(_TITLE_REGEX.search(segment))


def _is_plain_headline(line):
    if not 3 <= len(line) <= 100 or len(line.split()) > 12:
        return False
    if _looks_like_contact(line) or re.search(r"\d", line):
        return False
    if _HEADING_TO_SECTION.get(_normalize_heading(line)):
        return False
    return not line.rstrip().endswith(".")


def _find_title(lines, name, name_idx):
    for line in lines[:15]:
        for segment in _SEGMENT_SPLIT.split(line):
            segment = segment.strip()
            if segment and segment != name and _is_title_segment(segment):
                return segment
    if name_idx is not None and name_idx + 1 < len(lines):
        candidate = lines[name_idx + 1]
        if _is_plain_headline(candidate):
            return candidate
    return None


# --------------------------------------------------------------------------
# Bio / experience
# --------------------------------------------------------------------------
def _clean_bio(lines):
    text = " ".join(_BULLET.sub("", ln) for ln in lines)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) < 20:
        return None
    if len(text) > 500:
        cut = text[:500]
        end = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
        text = cut[: end + 1] if end > 150 else cut.rstrip() + "…"
    return text


_EXPLICIT_YEARS = [
    re.compile(r"(\d{1,2})(?:\.\d)?\s*\+?\s*(?:years?|yrs?)\b[^.\n]{0,50}?\bexperience", re.IGNORECASE),
    re.compile(r"\bexperience\b[^.\n]{0,30}?(\d{1,2})(?:\.\d)?\s*\+?\s*(?:years?|yrs?)\b", re.IGNORECASE),
]
_YEAR_RANGE = re.compile(
    r"\b((?:19|20)\d{2})\s*(?:-|–|—|to|until|till)\s*"
    r"(?:[A-Za-z]{3,9}\.?\s+|\d{1,2}[/.\-])?"
    r"((?:19|20)\d{2}|present|current|now|date|ongoing)\b",
    re.IGNORECASE,
)
_FRESHER = re.compile(
    r"\b(fresher|fresh graduate|recent graduate|entry[- ]level|"
    r"seeking (?:an? )?(?:internship|first (?:job|role)))\b",
    re.IGNORECASE,
)


def _years_of_experience(text, experience_lines):
    explicit = []
    for pattern in _EXPLICIT_YEARS:
        explicit += [int(m.group(1)) for m in pattern.finditer(text)]
    explicit = [y for y in explicit if 0 <= y <= 50]
    if explicit:
        return max(explicit)

    if not experience_lines:
        return None
    this_year = datetime.date.today().year
    spans = []
    for match in _YEAR_RANGE.finditer("\n".join(experience_lines)):
        start = int(match.group(1))
        end_raw = match.group(2)
        end = int(end_raw) if end_raw.isdigit() else this_year
        end = min(end, this_year)
        if 1970 <= start <= end:
            spans.append((start, end))
    if not spans:
        return None
    spans.sort()
    merged = [list(spans[0])]
    for start, end in spans[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return sum(end - start for start, end in merged)


def _level_from_years(years):
    if years < 2:
        return "Beginner"
    if years < 5:
        return "Intermediate"
    return "Expert"


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------
def _clean_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x0c", "\n")
    return text.replace("\xa0", " ").replace("\u200b", "").replace("\ufeff", "")


def _split_sections(lines):
    sections = {"header": []}
    current = "header"
    for line in lines:
        inline = _INLINE_HEADING.match(line)
        if inline:
            key = _HEADING_TO_SECTION.get(_normalize_heading(inline.group(1)))
            if key:
                current = key
                sections.setdefault(current, []).append(inline.group(2).strip())
                continue
        if len(line) <= 40:
            norm = _normalize_heading(line)
            key = _HEADING_TO_SECTION.get(norm)
            if key:
                current = key
                sections.setdefault(current, [])
                continue
            # Unknown ALL-CAPS multi-word line: treat as a heading that ends
            # the current section (e.g. "PROJECT WORK", "KEY ACHIEVEMENTS").
            words = line.split()
            if (current == "skills" and line.isupper() and 2 <= len(words) <= 4
                    and norm not in _VOCAB_LOOKUP and norm not in _ALIASES):
                current = "other"
                sections.setdefault(current, [])
                continue
        bucket = sections.setdefault(current, [])
        if current == "skills" and len(bucket) >= _MAX_SKILL_SECTION_LINES:
            continue
        bucket.append(line)
    return sections


def parse_cv(text):
    """
    Returns a dict containing only the fields that were detected, out of:
    name, title, bio, skills (list), experience ("Beginner" / "Intermediate"
    / "Expert"). Returns {} when the text is empty or nothing was recognised.
    """
    if not text or len(text.strip()) < 20:
        return {}

    text = _clean_text(text)
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    sections = _split_sections(lines)
    found = {}

    search_lines = sections.get("header") or lines
    name, name_idx = _find_name(search_lines)
    if name is None and search_lines is not lines:
        search_lines = lines
        name, name_idx = _find_name(search_lines)
    title = _find_title(search_lines, name, name_idx)
    if name:
        found["name"] = name
    if title:
        found["title"] = title

    bio = _clean_bio(sections.get("summary", []))
    if bio:
        found["bio"] = bio

    # Skip contact lines (emails, links, phone numbers) when scanning running
    # text so e.g. a "github.com/..." link isn't mistaken for a skill.
    scan_text = "\n".join(ln for ln in lines if not _looks_like_contact(ln))
    skills = _dedupe(_skill_tokens(sections.get("skills", [])) + _vocab_matches(scan_text))
    if skills:
        found["skills"] = skills[:MAX_SKILLS]

    years = _years_of_experience(text, sections.get("experience", []))
    if years is not None:
        found["experience"] = _level_from_years(years)
    elif _FRESHER.search(text):
        found["experience"] = "Beginner"

    return found


def describe_found(found):
    """Short human-readable list of what was detected, for the UI message."""
    labels = []
    if "name" in found:
        labels.append("name")
    if "title" in found:
        labels.append("title")
    if "bio" in found:
        labels.append("bio")
    if "skills" in found:
        labels.append(f"{len(found['skills'])} skills")
    if "experience" in found:
        labels.append(f"experience level ({found['experience']})")
    return labels
