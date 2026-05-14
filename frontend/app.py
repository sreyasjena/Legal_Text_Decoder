import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

# ── Page config must be the FIRST streamlit call ──
st.set_page_config(
    page_title="LexAI — Legal Intelligence",
    page_icon="⚖️",
    layout="wide",
)

# ── Session state defaults ──
from frontend.utils.session import init_session_state
init_session_state()

# ── Global CSS + SVG backgrounds (always rendered) ──
from frontend.styles.injector import inject_styles
inject_styles()

# ── Route to the correct page ──
from frontend.pages.landing   import show_landing
from frontend.pages.auth_page import show_auth
from frontend.pages.workspace import show_workspace

page = st.session_state.page

if page == "landing":
    show_landing()
elif page == "auth":
    show_auth()
elif page == "workspace":
    show_workspace()
