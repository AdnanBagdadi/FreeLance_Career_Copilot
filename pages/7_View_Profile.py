import streamlit as st
from utils.data import init_state
from utils.branding import apply_branding
from utils.auth import require_login, logout_button
from utils.storage import load_into_session

require_login()
apply_branding()
init_state()
load_into_session(st)
logout_button()

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
