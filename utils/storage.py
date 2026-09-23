import json
import sqlite3
from pathlib import Path

# --- Where the database file lives ---------------------------------------
# Sits in the project root, one level up from utils/. On Streamlit
# Community Cloud this file lives on the container's local disk: it
# survives page refreshes, new tabs, and multiple users hitting the same
# running app, but is WIPED whenever the app redeploys or wakes from
# sleep (a fresh container = a fresh, empty file). That's an intentional
# scope decision — true persistence across redeploys would need an
# external database instead of a local file.
DB_PATH = Path(__file__).resolve().parent.parent / "fcc_data.db"


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, value TEXT)")
    return conn


def _save(key, value):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO app_state (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, json.dumps(value)),
    )
    conn.commit()
    conn.close()


def _load(key, default):
    conn = _get_conn()
    row = conn.execute("SELECT value FROM app_state WHERE key = ?", (key,)).fetchone()
    conn.close()
    if row is None:
        return default
    return json.loads(row[0])


# --- Public save functions — call one right after mutating the matching
# session_state list/dict, so the database never falls out of sync. ------

def save_profile(profile):
    _save("profile", profile)


def save_portfolio(portfolio):
    _save("portfolio", portfolio)


def save_job_history(job_history):
    _save("job_history", job_history)


def save_applications(applications):
    _save("applications", applications)


def load_into_session(st):
    """
    Call once, right after utils.data.init_state(), on every page.
    init_state() sets its normal hardcoded defaults into a brand-new
    session's state first — this then overwrites those defaults with
    whatever was last saved to SQLite, if anything. Guarded by
    `_storage_loaded` so it only runs once per session rather than on
    every rerun (harmless either way, but avoids a redundant DB hit on
    every single interaction).
    """
    if st.session_state.get("_storage_loaded"):
        return

    if "profile" in st.session_state:
        st.session_state.profile = _load("profile", st.session_state.profile)
    if "portfolio" in st.session_state:
        st.session_state.portfolio = _load("portfolio", st.session_state.portfolio)
    if "job_history" in st.session_state:
        st.session_state.job_history = _load("job_history", st.session_state.job_history)
    if "applications" in st.session_state:
        st.session_state.applications = _load("applications", st.session_state.applications)

    st.session_state._storage_loaded = True
