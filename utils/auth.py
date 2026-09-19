import base64
import logging
import time
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# --- Demo credentials (prototype only) ---------------------------------
# NOTE: This is the FALLBACK used only if no st.secrets are configured.
# In a real deployment, set these under [auth] in .streamlit/secrets.toml
# instead of hardcoding them in source — see _get_credentials() below.
VALID_USERNAME = "example@123"
VALID_PASSWORD = "pass1234"

# --- NFR config: security thresholds ------------------------------------
MAX_LOGIN_ATTEMPTS = 3          # failed attempts allowed before lockout
LOCKOUT_SECONDS = 30            # how long a lockout lasts
SESSION_TIMEOUT_MINUTES = 15    # auto-logout after this much inactivity

# --- Lockout state lives at MODULE level, not st.session_state. ---------
# st.session_state is tied to one browser session and is wiped on a page
# refresh (Streamlit starts a fresh session on reload), which is exactly
# why the old lockout timer used to reset on refresh. Module-level
# variables live in the server process's memory instead, so they survive
# refreshes and are shared across anyone hitting this single demo login —
# which is the correct behaviour for a brute-force guard.
_login_attempts = 0
_lockout_until = 0.0

# --- NFR: Observability — audit logging ---------------------------------
# Every auth event (success, failure, lockout, timeout) is logged with a
# timestamp. On Streamlit Community Cloud this shows up in the app's
# "Manage app" log panel, giving a basic audit trail without a database.
logger = logging.getLogger("fcc_auth")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s | AUTH | %(levelname)s | %(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


def _get_credentials():
    """
    NFR: Security — externalized credentials.
    Prefers st.secrets (set via .streamlit/secrets.toml locally, or the
    'Secrets' panel on Streamlit Cloud) over the hardcoded fallback, so a
    real deployment never needs credentials committed to source control.
    """
    try:
        return st.secrets["auth"]["username"], st.secrets["auth"]["password"]
    except Exception:
        return VALID_USERNAME, VALID_PASSWORD


def _render_countdown(remaining_seconds):
    """
    Renders a countdown that actually ticks down once per second in the
    browser. A plain st.warning can't do this — Streamlit only re-renders
    on user interaction, so a normal element would freeze at whatever
    number it was first given. st.components.v1.html renders inside an
    iframe, which is allowed to run its own <script>, so the seconds
    count down live with zero extra server reruns. The real lockout check
    still happens in Python on submit — this is purely a UX display.
    """
    components.html(
        f"""
        <div id="lockout-box" style="
            font-family:Arial, Helvetica, sans-serif; font-size:14px;
            color:#FFFFFF; background:#000000; padding:12px 16px;
            border-radius:8px; border:1px solid #000000;">
            Too many failed attempts. Try again in <b><span id="secs">{remaining_seconds}</span>s</b>.
        </div>
        <script>
        let secs = {remaining_seconds};
        const secsEl = document.getElementById('secs');
        const box = document.getElementById('lockout-box');
        const timer = setInterval(function() {{
            secs -= 1;
            if (secs <= 0) {{
                clearInterval(timer);
                box.style.background = '#e7f7ee';
                box.style.border = '1px solid #bbf0d3';
                box.style.color = '#1a7f4e';
                box.innerHTML = "You can try logging in again now.";
            }} else {{
                secsEl.innerText = secs;
            }}
        }}, 1000);
        </script>
        """,
        height=55,
    )


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
        .navbar-brand span {font-size:18px; font-weight:800; color:#FFFFFF;}

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

    if st.session_state.pop("session_expired", False):
        st.info(f"You were logged out after {SESSION_TIMEOUT_MINUTES} minutes of inactivity. "
                "Please log in again.")

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

    # NFR: Security — brute-force lockout, backed by module-level state
    # (see comment near _lockout_until above) so it survives page refreshes.
    global _login_attempts, _lockout_until
    now = time.time()
    locked = now < _lockout_until

    if locked:
        _render_countdown(int(_lockout_until - now))

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter Your Username")
        password = st.text_input("Password", type="password", placeholder="Enter Your Password")
        submitted = st.form_submit_button("Log in", use_container_width=True)

    if submitted:
        # Re-check with a fresh timestamp at the moment of submission —
        # this is the authoritative check; the countdown above is just UX.
        now = time.time()
        if now < _lockout_until:
            remaining = int(_lockout_until - now)
            st.error(f"Still locked out. Try again in {remaining}s.")
        else:
            valid_username, valid_password = _get_credentials()
            if username == valid_username and password == valid_password:
                st.session_state.authenticated = True
                st.session_state.last_active = now
                _login_attempts = 0
                logger.info("Successful login for username='%s'.", username)
                st.rerun()
            else:
                _login_attempts += 1
                logger.warning("Failed login attempt %d for username='%s'.",
                                _login_attempts, username)
                if _login_attempts >= MAX_LOGIN_ATTEMPTS:
                    _lockout_until = now + LOCKOUT_SECONDS
                    _login_attempts = 0
                    logger.warning("Lockout triggered for %ds after %d failed attempts.",
                                    LOCKOUT_SECONDS, MAX_LOGIN_ATTEMPTS)
                    st.rerun()
                else:
                    remaining_tries = MAX_LOGIN_ATTEMPTS - _login_attempts
                    st.error(f"Incorrect username or password. {remaining_tries} attempt(s) "
                             "remaining before lockout.")

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

    NFR: Security — session timeout. An authenticated session that's been
    idle longer than SESSION_TIMEOUT_MINUTES is automatically logged out
    on its next page load, rather than staying valid indefinitely.
    """
    if st.session_state.get("authenticated", False):
        now = time.time()
        last_active = st.session_state.get("last_active", now)
        if now - last_active > SESSION_TIMEOUT_MINUTES * 60:
            logger.info("Session auto-expired after %d minutes of inactivity.",
                        SESSION_TIMEOUT_MINUTES)
            st.session_state.authenticated = False
            st.session_state.auth_view = "login"
            st.session_state.session_expired = True
        else:
            st.session_state.last_active = now
            return  # still valid — let the page render normally

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
