import streamlit as st


def apply_branding():
    """Puts the logo above the sidebar page-nav (must be called on every page)."""
    st.logo("assets/logo.png", icon_image="assets/favicon.png")
