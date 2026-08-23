# Freelance Career Copilot — Streamlit Prototype

An AI-assisted system for freelance job application support: paste or upload a job
description, compare it against your profile, see a transparent match score and
missing skills, get the right portfolio piece surfaced, and draft a personalized
proposal. It helps you prepare applications faster — it does not auto-submit
anything.

## Run
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Pages
- **My Profile** — skills, rate, experience, bio, and portfolio management
- **Analyze Job** — paste or upload a job description (.txt / .pdf / .docx)
- **Match Results** — score breakdown, matched/missing skills, plain-language
  "why this score" reasons, recommended portfolio piece
- **Proposal Generator** — tone-adjustable draft that references your matched
  skills and best-fit portfolio example
- **Applications** — tracker with status pipeline (Applied / Interviewing / Offer / …)
- **Insights** — skill-gap analysis aggregated across every job you've analyzed

## How this maps to the project brief
| Brief requirement | Where it lives |
|---|---|
| Accept freelancer profile, resume, portfolio | My Profile |
| Analyze a pasted/uploaded job description | Analyze Job |
| Compare job requirements to profile | Match Results |
| Match score + missing skills | Match Results |
| Explain *why* it's a fit (core differentiator) | Match Results → "Why this score" |
| Portfolio recommendation (core differentiator) | Match Results → recommended piece |
| Skill-gap analysis across multiple applications (core differentiator) | Insights |
| Personalized proposal draft | Proposal Generator |
| Application tracking (core differentiator) | Applications |

## Notes on this prototype
- Skill extraction from job text uses keyword matching against a skills list
  (`utils/skills_db.py`) — swap for an LLM call or NER model for production use.
- PDF/DOCX upload parsing is best-effort; paste-in text is the most reliable path
  in this prototype.
- All data is synthetic and stored only in Streamlit session state — nothing
  persists between sessions or reaches any real freelance platform.
