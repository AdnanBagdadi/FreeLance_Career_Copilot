import base64
from pathlib import Path
import streamlit as st

# --- Demo credentials (prototype only) ---------------------------------
# NOTE: This is a hardcoded check for prototype/demo purposes only.
# Do not use this pattern for a real deployment with real user data.
VALID_USERNAME = "example@123"
VALID_PASSWORD = "pass1234"

FEATURES = [
    ("🎯", "Transparent Match Scoring",
     "Paste any job description and get an explainable match percentage — not a black-box "
     "number — scored against your actual skills, rate and experience level."),
    ("🧠", "Recurring Skill-Gap Analytics",
     "Every missing skill is tallied across every job you analyze, so you always know exactly "
     "what's worth learning next."),
    ("📁", "Portfolio Piece Surfacing",
     "The most relevant sample from your portfolio is automatically recommended for each job, "
     "so you never guess what to showcase."),
    ("✍️", "Tailored Proposal Drafts",
     "Generate a first-pass proposal built directly from your match results, in the tone you "
     "want — ready to edit and send."),
    ("📊", "Application Tracking",
     "Track every proposal you've sent, its status through your pipeline, and revisit what "
     "you pitched at any time."),
    ("📈", "Insights Dashboard",
     "See your strongest skills and most common gaps across your entire job search, not just "
     "one application at a time."),
]


def _logo_b64():
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        return base64.b64encode(logo_path.read_bytes()).decode()
    return None


def _shared_css():
    st.markdown(
        """
        <style>
        #MainMenu, footer, header {visibility:hidden;}
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {display:none;}
        .block-container {padding-top:0; max-width:1100px;}

        .navbar {
            display:flex; align-items:center; justify-content:space-between;
            padding:18px 4px; margin-bottom:6px;
        }
        .navbar-brand {display:flex; align-items:center; gap:10px;}
        .navbar-brand img {width:32px; height:32px; border-radius:8px;}
        .navbar-brand span {font-size:18px; font-weight:800; color:#0f172a;}

        .hero {
            padding:46px 40px; border-radius:20px; margin:6px 0 34px 0;
            background:linear-gradient(135deg,#0f172a,#1e293b); color:white;
        }
        .hero h1 {font-size:38px; margin:0 0 12px 0;}
        .hero p {font-size:16.5px; color:#cbd5e1; max-width:680px; line-height:1.55;}

        .feat-grid {
            display:grid; grid-template-columns:repeat(3, 1fr);
            gap:18px; margin-top:6px;
        }
        .feat-card {
            padding:20px 20px 18px 20px; border:1px solid #e5e7eb; border-radius:14px;
            background:white; box-sizing:border-box;
        }
        .feat-card .emoji {font-size:26px;}
        .feat-card h4 {margin:10px 0 6px 0; font-size:16px; color:#0f172a;}
        .feat-card p {margin:0; font-size:12.8px; color:#6b7280; line-height:1.5;}

        .proto-banner {
            margin-top:36px; padding:14px 18px; border-radius:12px;
            background:#eef2ff; color:#4338ca; font-size:13px; text-align:center;
        }

        .login-title {font-size:26px; font-weight:800; color:#0f172a; margin:14px 0 4px 0;}
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


def _render_navbar():
    logo_b64 = _logo_b64()
    logo_html = f'<img src="data:image/png;base64,{logo_b64}">' if logo_b64 else "💼"
    left, right = st.columns([3, 1.4])
    with left:
        st.markdown(
            f'<div class="navbar-brand">{logo_html}<span>Freelance Career Copilot</span></div>',
            unsafe_allow_html=True,
        )
    with right:
        b1, b2 = st.columns(2)
        if b1.button("Log In", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()
        if b2.button("Sign Up", type="primary", use_container_width=True):
            st.session_state.auth_view = "signup"
            st.rerun()


def _render_landing():
    st.set_page_config(
        page_title="Freelance Career Copilot",
        page_icon="assets/favicon.png",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    _shared_css()
    _render_navbar()

    st.markdown(
        '<div class="hero"><h1>Know your fit before you apply</h1>'
        "<p>Freelance Career Copilot is an AI-assisted job-fit analysis and proposal drafting "
        "workspace. Paste any job description and get a transparent match score, see exactly "
        "what skills you're missing, get the right portfolio piece surfaced, and draft a "
        "tailored proposal — all in one pass.</p></div>",
        unsafe_allow_html=True,
    )

    st.subheader("Everything you need, in one workspace")
    cards_html = "".join(
        f'<div class="feat-card"><span class="emoji">{emoji}</span>'
        f'<h4>{title}</h4><p>{desc}</p></div>'
        for emoji, title, desc in FEATURES
    )
    st.markdown(f'<div class="feat-grid">{cards_html}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="proto-banner">Prototype demo — synthetic profile data, nothing is '
        "submitted anywhere. Log in or sign up above to try it.</div>",
        unsafe_allow_html=True,
    )

    st.stop()


def _render_login_form():
    st.set_page_config(
        page_title="Login • Freelance Career Copilot",
        page_icon="assets/favicon.png",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    _shared_css()

    st.markdown(
        """
        <style>
        .block-container {
            max-width:430px; margin-top:6vh;
            padding:38px 36px 32px 36px; background:white;
            border:1px solid #e5e7eb; border-radius:18px;
            box-shadow:0 10px 30px rgba(15,23,42,0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.button("← Back to home"):
        st.session_state.auth_view = "home"
        st.rerun()

    logo_b64 = _logo_b64()
    if logo_b64:
        st.markdown(
            f'<img src="data:image/png;base64,{logo_b64}" width="48" style="border-radius:12px;">',
            unsafe_allow_html=True,
        )

    is_signup = st.session_state.get("auth_view") == "signup"
    if is_signup:
        st.markdown('<p class="login-title">Create your account</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="login-sub">This prototype runs on one fixed demo account — '
            "sign up isn't wired to a real backend yet. Use the demo credentials below "
            "to continue.</p>",
            unsafe_allow_html=True,
        )
    else:
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
        "<b>example@123</b> / <b>pass1234</b> to sign in.</div>",
        unsafe_allow_html=True,
    )

    st.stop()


def require_login():
    """
    Gate the app behind a landing page + login screen.
    Call this as the very first thing on every page (app.py and each
    file in pages/), before any other st.* calls that render content.
    Stops execution with st.stop() until the user is authenticated.
    """
    if st.session_state.get("authenticated", False):
        return  # already logged in — let the page render normally

    view = st.session_state.get("auth_view", "home")
    if view in ("login", "signup"):
        _render_login_form()
    else:
        _render_landing()


def logout_button():
    """Optional: drop this in the sidebar of any page to let users sign out."""
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.auth_view = "home"
        st.rerun()
