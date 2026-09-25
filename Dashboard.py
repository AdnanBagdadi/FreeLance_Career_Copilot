import streamlit as st
from utils.data import init_state
from utils.branding import apply_branding
from utils.auth import require_login, logout_button
from utils.storage import load_into_session, save_job_history

require_login()  # must be the first Streamlit call — halts here until logged in

st.set_page_config(page_title="Freelance Career Copilot", page_icon="assets/favicon.png", layout="wide",
                    initial_sidebar_state="expanded")
apply_branding()
init_state()
load_into_session(st)
logout_button()

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
.card {
    padding:16px 18px;
    border:1px solid rgba(128, 128, 128, 0.25);
    border-radius:14px;
    background:var(--secondary-background-color);
    color:var(--text-color);
    height:140px;
    box-sizing:border-box;
    overflow:hidden;
}

.card h3 {
    color:var(--text-color);
    font-size:16px;
    margin:0 0 8px 0;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}

.card p {
    color:var(--text-color);
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] div.card) {
    gap:0.35rem;
}
.job {
    padding:18px;
    border:1px solid rgba(128,128,128,0.25);
    border-radius:14px;
    background:var(--secondary-background-color);
    color:var(--text-color);
    margin-bottom:12px;
}

.job h4 {
    color:var(--text-color);
}
.badge {display:inline-block; padding:5px 10px; border-radius:999px; background:#eef2ff; color:#4338ca; font-weight:700; font-size:12px;}
.small {
    color:var(--text-color);
    opacity:0.7;
    font-size:13px;
}
/* Force metric labels to follow active theme */
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label p,
div[data-testid="stMetric"] [data-testid="stMetricLabel"],
div[data-testid="stMetric"] [data-testid="stMetricLabel"] p {
    color: var(--text-color) !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.caption("AI-assisted job-fit analysis & proposal drafting")
st.sidebar.divider()
st.sidebar.success("Prototype Mode")
st.sidebar.caption("Synthetic profile data • no jobs are submitted anywhere")

profile = st.session_state.profile
history = st.session_state.job_history
apps = st.session_state.applications

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Jobs Analyzed", len(history))
    if st.button("View list", key="toggle_jobs_list"):
        st.session_state.show_jobs_list = not st.session_state.get("show_jobs_list", False)
c2.metric("Applications Tracked", len(apps))
c3.metric("Portfolio Pieces", len(st.session_state.portfolio))
avg = round(sum(h["score"] for h in history) / len(history)) if history else 0
c4.metric("Avg. Match Score", f"{avg}%")

if st.session_state.get("show_jobs_list", False):
    st.subheader("📋 All jobs analyzed")
    if st.session_state.pop("_job_deleted", False):
        st.success("Job removed from history.")
    if not history:
        st.info("No jobs analyzed yet — paste a job description to get your first match score.")
    else:
        for idx, h in enumerate(reversed(history)):
            with st.container(border=True):
                st.markdown(f"""
                <span class="badge">{h['score']}% MATCH</span>
                <h4 style="margin:8px 0 2px 0;">{h['title']}</h4>
                <p class="small">{len(h['matched'])} matched · {len(h['missing'])} missing skills</p>
                """, unsafe_allow_html=True)
                if st.button("🗑️ Delete", key=f"del_job_{idx}", help="Delete this job"):
                    st.session_state.job_history = [j for j in st.session_state.job_history if j is not h]
                    save_job_history(st.session_state.job_history)
                    st.session_state["_job_deleted"] = True
                    st.rerun()
    st.divider()

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

    p, q, r = st.columns(3)
    with p:
        st.markdown('<div class="card"><h3>4. 📊 Applications</h3><p class="small">Track every proposal '
                     'you\'ve sent and its status.</p></div>', unsafe_allow_html=True)
        if st.button("View applications", use_container_width=True):
            st.switch_page("pages/5_Applications.py")
    with q:
        st.markdown('<div class="card"><h3>5. 📈 Insights</h3><p class="small">See skill-gap patterns '
                     'across every job you\'ve analyzed.</p></div>', unsafe_allow_html=True)
        if st.button("View insights", use_container_width=True):
            st.switch_page("pages/6_Insights.py")

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
