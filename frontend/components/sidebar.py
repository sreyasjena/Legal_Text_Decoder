"""
frontend/components/sidebar.py
───────────────────────────────
Workspace sidebar component — configuration panel,
user info, language selector, back and logout buttons.
"""

import streamlit as st
from frontend.utils.session import go_landing, logout


def render_sidebar() -> str:
    """
    Render the workspace sidebar.
    Returns the selected language string.
    """
    with st.sidebar:
        # Title
        st.markdown(
            """
            <div style="font-family:'Rajdhani',sans-serif;font-size:24px;font-weight:700;
            color:var(--orange);padding-bottom:16px;
            border-bottom:1px solid rgba(255,140,66,0.15);margin-bottom:20px;">
                ⚙️ Configuration
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Logged-in user badge
        email = st.session_state.get("user_email", "Authenticated")
        st.markdown(
            f'<div class="user-badge" style="margin-bottom:20px;">👤 &nbsp; {email}</div>',
            unsafe_allow_html=True,
        )

        # Language selector
        st.markdown('<div class="sec-label">Output Language</div>', unsafe_allow_html=True)
        language = st.selectbox(
            "Language",
            ["English", "Hindi", "French", "German"],
            key="lang_sidebar",
            label_visibility="collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Supported formats info box
        st.markdown(
            """
            <div style="background:rgba(255,140,66,0.05);
            border:1px solid rgba(255,140,66,0.12);border-radius:14px;padding:18px;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:2px;
                color:var(--orange);text-transform:uppercase;margin-bottom:12px;">
                    Supported Formats
                </div>
                <div style="font-size:16px;color:var(--text2);line-height:2.4;">
                    📄 PDF Documents<br>
                    📝 Word (.docx)<br>
                    🖼️ Images (PNG/JPG)<br>
                    📃 Plain Text (.txt)<br>
                    ✍️ Direct Input
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Back to Home
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← Back to Home", key="ws_back_sb"):
            go_landing()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Log Out
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪  Log Out", key="ws_logout_sb"):
            logout()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    return language
