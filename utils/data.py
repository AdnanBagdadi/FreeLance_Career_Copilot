import streamlit as st


def _blank_profile():
    return {
        "name": "",
        "title": "",
        "bio": "",
        "skills": [],
        "experience": "Intermediate",
        "rate": 30,
    }


def init_state():
    """
    Sets blank/empty defaults into session state. This only fills gaps —
    it never overwrites data that's already there. For a first-time login,
    utils.storage.load_into_session() runs right after this and replaces
    these blanks with whatever that specific account has actually saved,
    if anything — so a brand-new account genuinely starts empty, and a
    returning account sees only its own data.
    """
    if "profile" not in st.session_state:
        st.session_state.profile = _blank_profile()
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = []
    if "job_history" not in st.session_state:
        st.session_state.job_history = []
    if "current_analysis" not in st.session_state:
        st.session_state.current_analysis = None
    if "applications" not in st.session_state:
        st.session_state.applications = []
    if "generated_proposal" not in st.session_state:
        st.session_state.generated_proposal = ""
