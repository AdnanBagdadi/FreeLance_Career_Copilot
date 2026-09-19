import streamlit as st
import base64
from pathlib import Path
from utils.data import init_state
from utils.branding import apply_branding
from utils.auth import require_login, logout_button

require_login()  # must be the first Streamlit call — halts here until logged in

st.set_page_config(page_title="Freelance Career Copilot", page_icon="assets/favicon.png", layout="wide",
                    initial_sidebar_state="expanded")
apply_branding()
init_state()
#logout_button()
# ---------- NAVBAR ----------
nav_logo, nav_title, nav_home, nav_profile, nav_analyze, nav_apps, nav_logout = st.columns(
    [0.4, 2.5, 0.8, 0.9, 1.1, 1.1, 0.9]
)

with nav_logo:
    st.image("assets/logo.png", width=38)

with nav_title:
    st.markdown("### Freelance Career Copilot")

with nav_home:
    if st.button("Home", use_container_width=True):
        st.switch_page("app.py")

with nav_profile:
    if st.button("Profile", use_container_width=True):
        st.switch_page("pages/1_👤_My_Profile.py")

with nav_analyze:
    if st.button("Analyze", use_container_width=True):
        st.switch_page("pages/2_📄_Analyze_Job.py")

with nav_apps:
    if st.button("Applications", use_container_width=True):
        st.switch_page("pages/5_📋_Applications.py")

with nav_logout:
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.auth_view = "home"
        st.rerun()

st.divider()

logo_b64 = base64.b64encode(Path("assets/logo.png").read_bytes()).decode()

st.markdown("""
<style>
#MainMenu, footer {visibility:hidden;}
.block-container {padding-top:1.5rem; max-width:1300px;}
.hero {padding:28px 30px; border-radius:18px; background:linear-gradient(135deg,#0f172a,#1e293b); color:white; margin-bottom:20px; display:flex; align-items:center; gap:22px;}
.hero img {width:64px; height:64px; border-radius:16px; flex-shrink:0;}
.hero h1 {font-size:38px; margin:0 0 8px 0;}
.hero p {font-size:16px; color:#cbd5e1;}
.sidebar-brand {display:flex; align-items:center; gap:10px; margin-bottom:2px;}
.sidebar-brand img {width:34px; height:34px; border-radius:9px;}
.sidebar-brand span {font-size:19px; font-weight:700; color:#0f172a;}
.card {padding:18px; border:1px solid #e5e7eb; border-radius:14px; background:white; min-height:130px;}
.job {padding:18px; border:1px solid #e5e7eb; border-radius:14px; background:white; margin-bottom:12px;}
.badge {display:inline-block; padding:5px 10px; border-radius:999px; background:#eef2ff; color:#4338ca; font-weight:700; font-size:12px;}
.small {color:#6b7280; font-size:13px;}
</style>
""", unsafe_allow_html=True)

st.sidebar.caption("AI-assisted job-fit analysis & proposal drafting")
st.sidebar.divider()
st.sidebar.success("Prototype Mode")
st.sidebar.caption("Synthetic profile data • no jobs are submitted anywhere")

st.markdown(f"""
<div class="hero">
<img src="data:image/png;base64,{logo_b64}">
<div>
<h1>Know your fit before you apply</h1>
<p>Paste any job description. Get a transparent match score, see exactly what skills you're missing,
get the right portfolio piece surfaced, and draft a tailored proposal — all in one pass.</p>
</div>
</div>
""", unsafe_allow_html=True)

profile = st.session_state.profile
history = st.session_state.job_history
apps = st.session_state.applications

c1, c2, c3, c4 = st.columns(4)
c1.metric("Jobs Analyzed", len(history))
c2.metric("Applications Tracked", len(apps))
c3.metric("Portfolio Pieces", len(st.session_state.portfolio))
avg = round(sum(h["score"] for h in history) / len(history)) if history else 0
c4.metric("Avg. Match Score", f"{avg}%")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🚀 Get started")
    x, y, z = st.columns(3)
    with x:
        st.markdown('<div class="card"><h3>1. 👤 Set up profile</h3><p class="small">Skills, rate, '
                     'experience and portfolio.</p></div>', unsafe_allow_html=True)
        if st.button("Edit profile", use_container_width=True):
            st.switch_page("pages/1_My_Profile.py")
    with y:
        st.markdown('<div class="card"><h3>2. 📄 Paste a job</h3><p class="small">Paste or upload a job '
                     'description to analyze.</p></div>', unsafe_allow_html=True)
        if st.button("Analyze a job", use_container_width=True):
            st.switch_page("pages/2_Analyze_Job.py")
    with z:
        st.markdown('<div class="card"><h3>3. ✍️ Get a proposal</h3><p class="small">Generate a tailored '
                     'draft from the match.</p></div>', unsafe_allow_html=True)
        if st.button("Go to proposals", use_container_width=True):
            st.switch_page("pages/4_Proposal_Generator.py")

    st.subheader("🕓 Recently analyzed")
    if not history:
        st.info("No jobs analyzed yet — paste a job description to get your first match score.")
    for h in reversed(history[-4:]):
        st.markdown(f"""
        <div class="job">
        <span class="badge">{h['score']}% MATCH</span>
        <h4 style="margin:8px 0 2px 0;">{h['title']}</h4>
        <p class="small">{len(h['matched'])} matched · {len(h['missing'])} missing skills</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("👤 Your profile")
    st.markdown(f"**{profile['name']}**")
    st.caption(profile["title"])
    st.write(f"Rate: **${profile['rate']}/hr** · Level: **{profile['experience']}**")
    st.caption("Skills: " + ", ".join(profile["skills"][:8]))

    st.subheader("📊 Top skill gaps")
    if history:
        from collections import Counter
        gaps = Counter(s for h in history for s in h["missing"])
        if gaps:
            for skill, count in gaps.most_common(5):
                st.write(f"⚠️ **{skill}** — missing in {count} job(s)")
        else:
            st.success("No recurring skill gaps across analyzed jobs.")
    else:
        st.caption("Analyze a few jobs to see recurring skill gaps here.")
