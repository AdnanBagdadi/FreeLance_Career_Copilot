import streamlit as st
from utils.data import init_state
from utils.branding import apply_branding
from utils.proposal_generator import generate_proposal

from utils.auth import require_login, logout_button
from utils.storage import load_into_session, save_applications
require_login()

apply_branding()
init_state()
load_into_session(st)
logout_button()

st.markdown(
    """
    <style>
    .st-key-sticky_back_nav {
        position: fixed !important;
        top: 4.5rem;
        left: 1rem;
        z-index: 9999;
    }
    .st-key-sticky_back_nav button {
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)
with st.container(key="sticky_back_nav"):
    if st.button("←", key="navbar_back"):
        st.switch_page("Dashboard.py")

st.title("✍️ Proposal Generator")

analysis = st.session_state.current_analysis
if not analysis:
    st.warning("Analyze a job first so the proposal can reference your actual match.")
    if st.button("Analyze a job"):
        st.switch_page("pages/2_Analyze_Job.py")
    st.stop()

st.caption(f"Drafting for: **{analysis['title']}** · {analysis['score']}% match")

tone = st.radio("Tone", ["Professional", "Confident"], horizontal=True)

if st.button("Generate draft", type="primary"):
    portfolio_item = analysis["recommended_portfolio"][0] if analysis.get("recommended_portfolio") else None
    st.session_state.generated_proposal = generate_proposal(
        analysis["title"], analysis["matched"], analysis["missing"],
        st.session_state.profile, portfolio_item, tone,
    )

if st.session_state.generated_proposal:
    edited = st.text_area("Proposal draft (editable)", st.session_state.generated_proposal, height=320)
    st.session_state.generated_proposal = edited
    st.download_button("⬇️ Download as .txt", edited, file_name="proposal.txt")

    if st.button("📤 Mark as applied / track this application"):
        st.session_state.applications.append({
            "job_title": analysis["title"],
            "score": analysis["score"],
            "status": "Applied",
            "proposal": edited,
        })
        save_applications(st.session_state.applications)
        st.success("Added to Applications tracker.")
