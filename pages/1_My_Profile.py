import streamlit as st
from utils.data import init_state
from utils.branding import apply_branding
from utils.storage import load_into_session, save_profile, save_portfolio
from utils.cv_parser import parse_cv, describe_found, merge_skills
from utils.jd_parser import read_uploaded_file

from utils.auth import require_login, logout_button
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

st.title("👤 My Profile")
st.caption("This is what your job description matches, missing skills and proposals are generated against.")

just_saved = st.session_state.pop("_profile_saved", False)
if just_saved:
    st.success("Profile saved successfully!")
if st.session_state.pop("_portfolio_added", False):
    st.success("Portfolio piece added.")
if st.session_state.pop("_portfolio_removed", False):
    st.success("Portfolio piece removed.")

cv_result = st.session_state.pop("_cv_result", None)
if cv_result == "none":
    st.warning("Couldn't confidently pull anything from that file — try filling the fields in below manually.")
elif cv_result:
    st.success("Pulled from your CV: " + ", ".join(cv_result) + ". Review the fields below, then Save profile.")

st.subheader("📤 Auto-fill from CV")
st.caption("Upload your resume and we'll try to pre-fill your name, title, bio, skills and "
           "experience level below — nothing is saved until you review it and click Save profile.")
cv_file = st.file_uploader("Upload CV (.txt, .pdf or .docx)", type=["txt", "pdf", "docx"], key="cv_uploader")
if cv_file is not None:
    if st.button("🪄 Auto-fill from this CV"):
        cv_text = read_uploaded_file(cv_file)
        found = parse_cv(cv_text)
        if not found:
            st.session_state["_cv_result"] = "none"
        else:
            updated = dict(st.session_state.profile)
            if "name" in found:
                updated["name"] = found["name"]
            if "title" in found:
                updated["title"] = found["title"]
            if "bio" in found:
                updated["bio"] = found["bio"]
            if "experience" in found:
                updated["experience"] = found["experience"]
            if "skills" in found:
                updated["skills"] = merge_skills(found["skills"], updated["skills"])
            st.session_state.profile = updated
            st.session_state["_cv_result"] = describe_found(found)
        st.rerun()

st.divider()

profile = st.session_state.profile

# Right after a successful save, show blank fields for one render as a
# visual "this went through" signal — the actual saved data in
# st.session_state.profile is untouched; only these displayed defaults
# are blanked. Revisiting the page afterwards shows the real saved values.
if just_saved:
    form_defaults = {"name": "", "title": "", "bio": "", "experience": "Beginner", "skills": []}
else:
    form_defaults = profile

with st.form("profile_form"):
    c1, c2 = st.columns(2)
    name = c1.text_input("Name", form_defaults["name"])
    title = c2.text_input("Title / headline", form_defaults["title"])
    bio = st.text_area("Bio", form_defaults["bio"], height=80)

    experience = st.selectbox("Experience level", ["Beginner", "Intermediate", "Expert"],
                               index=["Beginner", "Intermediate", "Expert"].index(form_defaults["experience"]))

    skills_text = st.text_area("Skills (comma-separated)", ", ".join(form_defaults["skills"]), height=80)

    submitted = st.form_submit_button("💾 Save profile", type="primary")
    if submitted:
        new_skills = [s.strip() for s in skills_text.split(",") if s.strip()]
        if not name.strip():
            st.error("Please enter your name before saving.")
        elif not new_skills:
            st.error("Please add at least one skill before saving.")
        else:
            st.session_state.profile = {
                "name": name, "title": title, "bio": bio,
                "experience": experience, "rate": profile["rate"],
                "skills": new_skills,
            }
            save_profile(st.session_state.profile)
            st.session_state["_profile_saved"] = True
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
            save_portfolio(st.session_state.portfolio)
            st.session_state["_portfolio_removed"] = True
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
                save_portfolio(st.session_state.portfolio)
                st.session_state["_portfolio_added"] = True
                st.rerun()
            else:
                st.warning("Give it a title first.")
