import hashlib
import hmac
import json
import os
import sqlite3
from pathlib import Path

import streamlit as st

# --- Where the database file lives ---------------------------------------
# Sits in the project root, one level up from utils/. On Streamlit
# Community Cloud this file lives on the container's local disk: it
# survives page refreshes, new tabs, and multiple users hitting the same
# running app, but is WIPED whenever the app redeploys or wakes from
# sleep (a fresh container = a fresh, empty file). That's an intentional
# scope decision — true persistence across redeploys would need an
# external database instead of a local file.
DB_PATH = Path(__file__).resolve().parent.parent / "fcc_data.db"

# A brand-new account starts completely blank — no sample name, skills,
# rate, etc. This is what a first-time sign-up sees on My Profile / View
# Profile, instead of inheriting whatever utils/data.py's init_state()
# seeds by default for a fresh session.
BLANK_PROFILE = {"name": "", "title": "", "bio": "", "experience": "Beginner", "rate": 5, "skills": []}


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, salt TEXT NOT NULL, "
        "password_hash TEXT NOT NULL)"
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


def _current_username():
    return st.session_state.get("username", "anonymous")


def _user_key(name):
    return f"user:{_current_username()}:{name}"


# --- Real user accounts, hashed (stdlib only — no new dependency) --------

def _hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000).hex()
    return salt, digest


def user_exists(username):
    conn = _get_conn()
    row = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row is not None


def create_user(username, password):
    """Returns True if the account was created, False if the username is taken."""
    if user_exists(username):
        return False
    salt, digest = _hash_password(password)
    conn = _get_conn()
    conn.execute("INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
                 (username, salt, digest))
    conn.commit()
    conn.close()
    return True


def verify_user(username, password):
    conn = _get_conn()
    row = conn.execute("SELECT salt, password_hash FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if row is None:
        return False
    salt, stored_digest = row
    _, digest = _hash_password(password, salt)
    return hmac.compare_digest(digest, stored_digest)


def ensure_seed_account(username, password):
    """Seeds a built-in account (e.g. the demo login) if it doesn't exist yet."""
    if not user_exists(username):
        create_user(username, password)


def delete_user(username):
    """
    Permanently deletes the account AND every piece of data saved under
    it (profile, portfolio, job history, applications). This cannot be
    undone — there is no recovery/undo table. Call this only after the
    user has explicitly confirmed they want their account gone.
    """
    prefix = f"user:{username}:"
    conn = _get_conn()
    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    # Not using SQL LIKE here: '_' is a wildcard in LIKE patterns, and a
    # username containing an underscore (e.g. "jane_doe") would then
    # match other users' keys too. Filtering the exact prefix in Python
    # avoids that entirely.
    all_keys = [row[0] for row in conn.execute("SELECT key FROM app_state").fetchall()]
    keys_to_delete = [k for k in all_keys if k.startswith(prefix)]
    conn.executemany("DELETE FROM app_state WHERE key = ?", [(k,) for k in keys_to_delete])
    conn.commit()
    conn.close()


# --- Public save functions — call one right after mutating the matching
# session_state list/dict, so the database never falls out of sync.
# Each is scoped to whichever username is currently logged in, read
# internally via st.session_state — callers don't need to pass it. -------

def save_profile(profile):
    _save(_user_key("profile"), profile)


def save_portfolio(portfolio):
    _save(_user_key("portfolio"), portfolio)


def save_job_history(job_history):
    _save(_user_key("job_history"), job_history)


def save_applications(applications):
    _save(_user_key("applications"), applications)


def load_into_session(st_module):
    """
    Call once, right after utils.data.init_state(), on every page.
    init_state() sets its normal hardcoded defaults into a brand-new
    session's state first — this then overwrites those defaults with
    whatever this specific logged-in user last saved to SQLite, or a
    blank slate if they're a first-time account. Guarded by
    `_storage_loaded` so it only runs once per session rather than on
    every rerun.
    """
    if st_module.session_state.get("_storage_loaded"):
        return
    if not st_module.session_state.get("username"):
        return  # not logged in yet — require_login() should prevent reaching here anyway

    profile = _load(_user_key("profile"), None)
    st_module.session_state.profile = profile if profile is not None else dict(BLANK_PROFILE)

    portfolio = _load(_user_key("portfolio"), None)
    st_module.session_state.portfolio = portfolio if portfolio is not None else []

    job_history = _load(_user_key("job_history"), None)
    st_module.session_state.job_history = job_history if job_history is not None else []

    applications = _load(_user_key("applications"), None)
    st_module.session_state.applications = applications if applications is not None else []

    st_module.session_state._storage_loaded = True
