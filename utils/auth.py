import base64
from pathlib import Path
import streamlit as st

# --- Demo credentials (prototype only) ---------------------------------
# NOTE: This is a hardcoded check for prototype/demo purposes only.
# Do not use this pattern for a real deployment with real user data.
VALID_USERNAME = "example@123"
VALID_PASSWORD = "pass1234"


def require_login():
    """
    Gate the app behind a simple login screen.
    Call this as the very first thing on every page (app.py and each
    file in pages/), before any other st.* calls that render content.
    Stops execution with st.stop() until the user is authenticated.
    """
    if st.session_state.get("authenticated", False):
        return  # already logged in — let the page render normally

    st.set_page_config(
        page_title="Login • Freelance Career Copilot",
        page_icon="assets/favicon.png",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    st.markdown(
        """
        <style>
        #MainMenu, footer, header {visibility:hidden;}
        .block-container {padding-top:8vh; max-width:420px;}
        .login-card {
            padding:36px 34px 30px 34px; border-radius:18px;
            background:white; border:1px solid #e5e7eb;
            box-shadow:0 10px 30px rgba(15,23,42,0.08);
        }
        .login-title {font-size:26px; font-weight:800; color:#0f172a; margin:0 0 4px 0;}
        .login-sub {font-size:13.5px; color:#6b7280; margin:0 0 22px 0;}
        .login-hint {
            margin-top:18px; padding:10px 14px; border-radius:10px;
            background:#eef2ff; color:#4338ca; font-size:12.5px;
        }
        div[data-testid="stForm"] {border:none; padding:0;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    logo_path = Path("assets/logo.png")
    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    if logo_path.exists():
        logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
        st.markdown(
            f'<img src="data:image/png;base64,{logo_b64}" width="48" '
            f'style="border-radius:12px; margin-bottom:14px;">',
            unsafe_allow_html=True,
        )

    st.markdown('<p class="login-title">Welcome back</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="login-sub">Sign in to your Freelance Career Copilot workspace.</p>',
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="example@123")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Log in", use_container_width=True)

    if submitted:
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect username or password. Please try again.")

    st.markdown(
        '<div class="login-hint">Prototype demo — use '
        '<b>example@123</b> / <b>pass1234</b> to sign in.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()  # halt so nothing below this point renders while logged out


def logout_button():
    """Optional: drop this in the sidebar of any page to let users sign out."""
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
