import json
import sqlite3
from datetime import datetime, timezone
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
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "username TEXT PRIMARY KEY, password_hash TEXT NOT NULL, created_at TEXT)"
    )
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


# --- Accounts --------------------------------------------------------------
# A real, persisted users table, separate from the per-user app data below.
# Signing up writes a new row here; logging in checks against it.

def user_exists(username):
    conn = _get_conn()
    row = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row is not None


def create_user(username, password_hash):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, password_hash, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def get_password_hash(username):
    conn = _get_conn()
    row = conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row[0] if row else None


# --- Public save functions — every key is namespaced by username, so each
# account gets its own profile/portfolio/history/applications. Call one
# right after mutating the matching session_state list/dict, so the
# database never falls out of sync. -----------------------------------------

def save_profile(username, profile):
    _save(f"profile:{username}", profile)


def save_portfolio(username, portfolio):
    _save(f"portfolio:{username}", portfolio)


def save_job_history(username, job_history):
    _save(f"job_history:{username}", job_history)


def save_applications(username, applications):
    _save(f"applications:{username}", applications)


def load_into_session(st, username):
    """
    Call once per login, right after utils.data.init_state(), on every page.
    init_state() sets its normal blank defaults into a brand-new session's
    state first — this then overwrites those defaults with whatever THIS
    username last saved to SQLite, if anything, so one account never sees
    another account's data. Guarded per-username so it only runs once per
    session rather than on every rerun (harmless either way, but avoids a
    redundant DB hit on every single interaction) — and so that logging
    out and back in as a *different* user in the same browser tab correctly
    reloads, since the guard key includes the username.
    """
    loaded_key = f"_storage_loaded:{username}"
    if st.session_state.get(loaded_key):
        return

    st.session_state.profile = _load(f"profile:{username}", st.session_state.profile)
    st.session_state.portfolio = _load(f"portfolio:{username}", st.session_state.portfolio)
    st.session_state.job_history = _load(f"job_history:{username}", st.session_state.job_history)
    st.session_state.applications = _load(f"applications:{username}", st.session_state.applications)

    st.session_state[loaded_key] = True
