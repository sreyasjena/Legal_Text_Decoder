import streamlit as st

# ─────────────────────────────────────────────────────────
# DEFAULT SESSION STATE VALUES
# All keys that the app needs — set once on first load.
# Streamlit preserves these across reruns automatically.
# ─────────────────────────────────────────────────────────
DEFAULTS = {
    "page":             "landing",   # landing | auth | workspace
    "auth_tab":         "login",     # login | signup
    "auth_method":      "email",     # email | phone
    "otp_sent":         False,
    "pending_email":    "",
    "pending_phone":    "",
    "user_email":       "",
    "user_uid":         "",
    "logged_in":        False,       # stays True until explicit logout
    "pipeline_stage":   None,
    "result":           None,
    "email_link_debug": "",
}

def init_session_state():
    """Initialise every session key that hasn't been set yet."""
    for key, default in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default


# ─────────────────────────────────────────────────────────
# NAVIGATION HELPERS
# ─────────────────────────────────────────────────────────
def go_landing():
    st.session_state.page = "landing"

def go_auth(tab: str = "login"):
    st.session_state.page     = "auth"
    st.session_state.auth_tab = tab
    st.session_state.otp_sent = False

def go_workspace():
    st.session_state.page = "workspace"

def logout():
    """Full logout — wipes auth state and returns to landing."""
    for key, default in DEFAULTS.items():
        st.session_state[key] = default
    st.session_state.page = "landing"
