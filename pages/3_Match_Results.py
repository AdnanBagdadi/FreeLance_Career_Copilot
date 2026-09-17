import streamlit as st
from utils.data import init_state
from utils.branding import apply_branding

from utils.auth import require_login
require_login()

apply_branding()
init_state()

st.title("🎯 Match Results")

analysis = st.session_state.current_analysis
if not analysis:
    st.warning("No job analyzed yet.")
    if st.button("Analyze a job"):
        st.switch_page("pages/2_Analyze_Job.py")
    st.stop()

st.subheader(analysis["title"])
score = analysis["score"]
color = "🟢" if score >= 85 else ("🟡" if score >= 65 else "🔴")
c1, c2, c3 = st.columns(3)
c1.metric("AI Match Score", f"{score}%", delta=None)
c2.metric("Matched Skills", len(analysis["matched"]))
c3.metric("Missing Skills", len(analysis["missing"]))
st.write(f"{color} Overall fit for this role")

x, y = st.columns(2)
with x:
    st.success("✅ Matching skills")
    if analysis["matched"]:
        for s in analysis["matched"]:
            st.write("•", s)
    else:
        st.caption("No direct skill matches detected.")
with y:
    st.warning("⚠️ Skills to develop")
    if analysis["missing"]:
        for s in analysis["missing"]:
            st.write("•", s)
    else:
        st.caption("No skill gaps — you cover everything listed.")

st.divider()
st.subheader("💡 Why this score")
for r in analysis["reasons"]:
    st.write("•", r)

st.divider()
st.subheader("📁 Recommended portfolio piece")
recs = analysis.get("recommended_portfolio", [])
if recs:
    for item in recs:
        st.markdown(f"**{item['title']}**")
        st.write(item["description"])
        st.caption("Relevant skills: " + ", ".join(item["skills"]))
else:
    st.caption("Add portfolio pieces on the Profile page to get recommendations here.")

st.divider()
if st.button("✍️ Generate proposal for this job", type="primary"):
    st.switch_page("pages/4_Proposal_Generator.py")
