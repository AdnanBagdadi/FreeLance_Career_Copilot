import streamlit as st
from collections import Counter
from utils.data import init_state
from utils.branding import apply_branding

from utils.auth import require_login, logout_button
require_login()

apply_branding()
init_state()
logout_button()

st.title("📈 Insights")
st.caption("Skill-gap patterns across every job you've analyzed — not just one application at a time.")

history = st.session_state.job_history
if not history:
    st.info("Analyze a few jobs to unlock skill-gap insights.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Jobs analyzed", len(history))
c2.metric("Avg. match score", f"{round(sum(h['score'] for h in history)/len(history))}%")
strong = len([h for h in history if h["score"] >= 85])
c3.metric("Strong matches (85%+)", strong)

st.subheader("⚠️ Most common missing skills")
gaps = Counter(s for h in history for s in h["missing"])
if gaps:
    for skill, count in gaps.most_common(10):
        pct = round(count / len(history) * 100)
        st.write(f"**{skill}** — appeared missing in {count}/{len(history)} jobs ({pct}%)")
        st.progress(pct / 100)
else:
    st.success("No recurring skill gaps — your profile covers what these jobs ask for.")

st.subheader("✅ Most valuable skills you already have")
strengths = Counter(s for h in history for s in h["matched"])
if strengths:
    for skill, count in strengths.most_common(10):
        st.write(f"**{skill}** — matched in {count}/{len(history)} jobs")
else:
    st.caption("No matched skills recorded yet.")

st.subheader("🗂️ All analyzed jobs")
for h in reversed(history):
    st.write(f"**{h['title']}** — {h['score']}% match, missing: "
              f"{', '.join(h['missing']) if h['missing'] else 'none'}")
