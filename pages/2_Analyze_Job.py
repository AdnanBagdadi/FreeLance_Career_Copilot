import streamlit as st
from utils.data import init_state
from utils.branding import apply_branding
from utils.jd_parser import extract_skills, extract_experience_level, extract_budget, read_uploaded_file
from utils.scoring import calculate_match, matched_skills, missing_skills, match_reasons
from utils.portfolio import recommend_portfolio

from utils.auth import require_login, logout_button
from utils.storage import load_into_session, save_job_history
require_login()

apply_branding()
init_state()
load_into_session(st)
logout_button()
st.title("📄 Analyze a Job Description")
st.caption("Paste the job post, or upload a file. Nothing is submitted anywhere — this only analyzes.")

job_title = st.text_input("Job title (optional, for your own tracking)", placeholder="e.g. Python ML Developer")

tab1, tab2 = st.tabs(["Paste text", "Upload file"])
jd_text = ""
with tab1:
    jd_text = st.text_area("Paste the full job description", height=260,
                            placeholder="Paste the job post here...")
with tab2:
    up = st.file_uploader("Upload a .txt, .pdf or .docx job description", type=["txt", "pdf", "docx"])
    if up is not None:
        jd_text = read_uploaded_file(up)
        st.text_area("Extracted text (edit if needed)", value=jd_text, height=200, key="extracted_preview")
        jd_text = st.session_state.get("extracted_preview", jd_text)

if st.button("Analyze Job", type="primary"):
    if not jd_text.strip():
        st.warning("Paste or upload a job description first.")
    else:
        profile = st.session_state.profile
        job_skills = extract_skills(jd_text)
        exp_level = extract_experience_level(jd_text)
        budget = extract_budget(jd_text)
        score = calculate_match(job_skills, budget, exp_level, profile)
        matched = matched_skills(job_skills, profile)
        missing = missing_skills(job_skills, profile)
        reasons = match_reasons(job_skills, budget, exp_level, profile, score)
        recs = recommend_portfolio(job_skills, st.session_state.portfolio)

        analysis = {
            "title": job_title.strip() or "Untitled job",
            "jd_text": jd_text,
            "skills": job_skills,
            "exp_level": exp_level,
            "budget": budget,
            "score": score,
            "matched": matched,
            "missing": missing,
            "reasons": reasons,
            "recommended_portfolio": recs,
        }
        st.session_state.current_analysis = analysis
        st.session_state.job_history.append(analysis)
        save_job_history(st.session_state.job_history)
        st.switch_page("pages/3_Match_Results.py")

if not jd_text.strip():
    st.info("Paste or upload a job description, then click **Analyze Job**.")
