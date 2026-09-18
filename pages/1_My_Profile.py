import streamlit as st
from utils.data import init_state
from utils.branding import apply_branding

from utils.auth import require_login, logout_button
require_login()
apply_branding()
init_state()
logout_button()

st.title("👤 My Profile")
st.caption("This is what your job description matches, missing skills and proposals are generated against.")

profile = st.session_state.profile

with st.form("profile_form"):
    c1, c2 = st.columns(2)
    name = c1.text_input("Name", profile["name"])
    title = c2.text_input("Title / headline", profile["title"])
    bio = st.text_area("Bio", profile["bio"], height=80)

    c3, c4 = st.columns(2)
    experience = c3.selectbox("Experience level", ["Beginner", "Intermediate", "Expert"],
                               index=["Beginner", "Intermediate", "Expert"].index(profile["experience"]))
    rate = c4.number_input("Hourly rate ($)", min_value=5, max_value=300, value=profile["rate"])

    skills_text = st.text_area("Skills (comma-separated)", ", ".join(profile["skills"]), height=80)

    submitted = st.form_submit_button("💾 Save profile", type="primary")
    if submitted:
        st.session_state.profile = {
            "name": name, "title": title, "bio": bio,
            "experience": experience, "rate": rate,
            "skills": [s.strip() for s in skills_text.split(",") if s.strip()],
        }
        st.success("Profile saved.")
        st.rerun()

st.divider()
st.subheader("📁 Portfolio")
st.caption("Used to recommend the best example to reference in each proposal.")

for item in st.session_state.portfolio:
    with st.container():
        st.markdown(f"**{item['title']}**")
        st.write(item["description"])
        st.caption("Skills: " + ", ".join(item["skills"]))
        if st.button("🗑️ Remove", key=f"rm_{item['id']}"):
            st.session_state.portfolio = [p for p in st.session_state.portfolio if p["id"] != item["id"]]
            st.rerun()
        st.divider()

with st.expander("➕ Add a portfolio piece"):
    with st.form("add_portfolio"):
        p_title = st.text_input("Title")
        p_desc = st.text_area("Description", height=70)
        p_skills = st.text_input("Skills (comma-separated)")
        if st.form_submit_button("Add"):
            if p_title.strip():
                new_id = max([p["id"] for p in st.session_state.portfolio], default=0) + 1
                st.session_state.portfolio.append({
                    "id": new_id, "title": p_title,
                    "description": p_desc,
                    "skills": [s.strip() for s in p_skills.split(",") if s.strip()],
                })
                st.success("Added.")
                st.rerun()
            else:
                st.warning("Give it a title first.")
