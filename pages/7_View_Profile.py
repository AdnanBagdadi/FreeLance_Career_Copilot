import streamlit as st
from utils.data import init_state
from utils.branding import apply_branding
from utils.auth import require_login, logout_button
from utils.storage import load_into_session, delete_user

require_login()
apply_branding()
init_state()
load_into_session(st)
logout_button()

nav_back, nav_spacer = st.columns([1, 10])
with nav_back:
    if st.button("←", key="navbar_back"):
        st.switch_page("Dashboard.py")


st.title("👤 View Profile")
st.caption("A read-only summary of your profile. Use Edit Profile below to make changes.")

profile = st.session_state.profile

st.subheader(profile["name"] or "—")
st.caption(profile["title"] or "No title set yet.")
st.write(profile["bio"] or "_No bio added yet._")

c1, c2 = st.columns(2)
c1.metric("Experience level", profile["experience"])
c2.metric("Hourly rate", f"${profile['rate']}/hr")

st.write("**Skills:** " + (", ".join(profile["skills"]) if profile["skills"] else "No skills added yet."))

st.divider()
st.subheader("📁 Portfolio")
if not st.session_state.portfolio:
    st.caption("No portfolio pieces added yet.")
else:
    for item in st.session_state.portfolio:
        with st.container(border=True):
            st.markdown(f"**{item['title']}**")
            st.write(item["description"])
            st.caption("Skills: " + ", ".join(item["skills"]))

st.divider()
if st.button("✏️ Edit Profile", use_container_width=True):
    st.switch_page("pages/1_My_Profile.py")

st.divider()
with st.expander("⚠️ Deactivate Account"):
    st.write("Permanently delete your account and everything saved under it — profile, "
             "portfolio, job history, and applications. **This cannot be undone.**")
    confirm = st.checkbox("I understand this will permanently delete my account and all my data.")
    if st.button("Delete My Account", type="primary", disabled=not confirm):
        username = st.session_state.get("username")
        delete_user(username)
        st.session_state.authenticated = False
        st.session_state.auth_view = "home"
        st.session_state.pop("username", None)
        st.session_state.pop("_storage_loaded", None)
        st.rerun()
