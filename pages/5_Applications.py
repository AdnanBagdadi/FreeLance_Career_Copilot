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

st.title("📊 Applications")
st.caption("Track everything you've applied to and where it stands.")

apps = st.session_state.applications
if not apps:
    st.info("No applications tracked yet. Generate a proposal and click **Mark as applied**.")
else:
    for i, app in enumerate(apps):
        with st.container():
            c1, c2, c3 = st.columns([3, 1.3, 1])
            c1.markdown(f"**{app['job_title']}**  ·  {app['score']}% match")
            c2.markdown(f"**{app['status']}**")
            if c3.button("🗑️ Delete", key=f"del_{i}", use_container_width=True):
                st.session_state.applications = [a for a in apps if a is not app]
                save_applications(st.session_state.applications)
                st.success("Application removed.")
                st.rerun()
            with st.expander("View proposal sent"):
                st.write(app["proposal"])
            st.divider()
