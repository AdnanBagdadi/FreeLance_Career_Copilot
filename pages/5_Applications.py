import streamlit as st
from utils.data import init_state
from utils.branding import apply_branding

from utils.auth import require_login, logout_button
from utils.storage import load_into_session, save_applications
require_login()

apply_branding()
init_state()
load_into_session(st)
logout_button()

st.title("📊 Applications")
st.caption("Track everything you've applied to and where it stands.")

apps = st.session_state.applications
if not apps:
    st.info("No applications tracked yet. Generate a proposal and click **Mark as applied**.")
else:
    statuses = ["Applied", "Interviewing", "Offer", "Rejected", "Withdrawn"]
    for i, app in enumerate(apps):
        with st.container():
            c1, c2, c3 = st.columns([3, 1.3, 1])
            c1.markdown(f"**{app['job_title']}**  ·  {app['score']}% match")
            new_status = c2.selectbox("Status", statuses, index=statuses.index(app["status"]),
                                       key=f"status_{i}", label_visibility="collapsed")
            if new_status != app["status"]:
                app["status"] = new_status
                save_applications(apps)
            if c3.button("🗑️ Delete", key=f"del_{i}", use_container_width=True):
                st.session_state.applications = [a for a in apps if a is not app]
                save_applications(st.session_state.applications)
                st.success("Application removed.")
                st.rerun()
            with st.expander("View proposal sent"):
                st.write(app["proposal"])
            st.divider()

    st.subheader("📈 Pipeline overview")
    from collections import Counter
    counts = Counter(a["status"] for a in apps)
    cols = st.columns(len(statuses))
    for col, s in zip(cols, statuses):
        col.metric(s, counts.get(s, 0))
