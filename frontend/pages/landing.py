"""
frontend/pages/landing.py
──────────────────────────
Landing page — hero section, feature cards, stats,
logged-in banner, and CTA buttons.
"""

import streamlit as st
from frontend.utils.session import go_auth, go_workspace, logout
from frontend.components.ticker import render_ticker


def show_landing():
    """Render the full landing page."""

    # ── LOGGED-IN BANNER ──────────────────────────────────
    if st.session_state.logged_in:
        user_display = st.session_state.user_email or "Authenticated User"
        if len(user_display) > 35:
            user_display = user_display[:33] + "…"

        st.markdown(
            f"""
            <div class="logged-in-banner">
                <div class="banner-left">
                    <div class="banner-avatar">👤</div>
                    <div class="banner-info">
                        <div class="banner-status">
                            <span class="banner-pulse"></span> Logged In
                        </div>
                        <div class="banner-email">{user_display}</div>
                    </div>
                </div>
                <div class="banner-right">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
                    color:var(--text2);letter-spacing:1px;">
                        Session active — click to continue
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        wb1, wb2, wb3, wb4 = st.columns([0.5, 1, 0.6, 0.5])
        with wb2:
            st.markdown('<div class="cta-workspace">', unsafe_allow_html=True)
            if st.button("🚀  Go to Workspace", key="go_ws_banner"):
                go_workspace(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with wb3:
            st.markdown('<div class="logout-btn" style="margin-top:8px;">', unsafe_allow_html=True)
            if st.button("🚪  Log Out", key="logout_banner"):
                logout(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # ── EYEBROW ──────────────────────────────────────────
    e1, e2, e3 = st.columns([1, 2, 1])
    with e2:
        st.markdown(
            """
            <div style="display:flex;justify-content:center;margin-top:20px;">
                <div class="land-eyebrow">
                    ⬡ &nbsp; AI-Powered Legal Intelligence Platform &nbsp; ⬡
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── MEGA TITLE ───────────────────────────────────────
    st.markdown(
        """
        <div class="lexai-wrap">
            <div class="lexai-ghost">LEXAI</div>
            <div class="lexai-title">LEXAI</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="land-title-sub">Legal Intelligence · Decoded</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="scan-line"></div>', unsafe_allow_html=True)

    # ── DESCRIPTION ──────────────────────────────────────
    d1, d2, d3 = st.columns([1, 3, 1])
    with d2:
        st.markdown(
            """
            <div class="land-desc">
                Upload contracts, NDAs, or any legal document — our AI decodes complex
                legalese into crystal-clear insights using RAG, multilingual LLMs, and
                voice synthesis. Watch the entire AI pipeline run live, step by step.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── STATS ────────────────────────────────────────────
    st.markdown(
        """
        <div class="land-stats">
            <div class="stat-box"><span class="stat-val">RAG</span><span class="stat-lbl">Powered</span></div>
            <div class="stat-box"><span class="stat-val">4</span><span class="stat-lbl">Languages</span></div>
            <div class="stat-box"><span class="stat-val">5+</span><span class="stat-lbl">File Types</span></div>
            <div class="stat-box"><span class="stat-val">∞</span><span class="stat-lbl">Insights</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── FEATURE CARDS ────────────────────────────────────
    cards = [
        ("🧠", "RAG Analysis",
         "Searches 12,000+ legal documents to ground every insight in statute and precedent."),
        ("🌍", "Multilingual",
         "Full legal analysis in English, Hindi, French, or German — no language barrier."),
        ("🔊", "Voice Output",
         "AI voice synthesis reads the full analysis aloud in your chosen language."),
        ("🔬", "Pipeline View",
         "Watch every AI step live — extraction, retrieval, augmentation, and generation."),
    ]
    fc1, fc2, fc3, fc4 = st.columns(4, gap="medium")
    for col, (icon, title, text) in zip([fc1, fc2, fc3, fc4], cards):
        with col:
            st.markdown(
                f"""
                <div class="feat-card">
                    <div class="hex-corner"></div>
                    <div class="hex-corner-bl"></div>
                    <span class="feat-icon">{icon}</span>
                    <div class="feat-title">{title}</div>
                    <div class="feat-text">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CTA BUTTONS ──────────────────────────────────────
    if st.session_state.logged_in:
        cl, cc, cr = st.columns([1.5, 1, 1.5])
        with cc:
            st.markdown('<div class="cta-workspace">', unsafe_allow_html=True)
            if st.button("🚀  Enter Workspace", key="go_ws_main"):
                go_workspace(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        bl, bc1, bc2, br = st.columns([1.2, 0.9, 0.9, 1.2])
        with bc1:
            st.markdown('<div class="btn-login">', unsafe_allow_html=True)
            if st.button("🔑  Log In", key="land_login"):
                go_auth("login"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with bc2:
            st.markdown('<div class="btn-signup">', unsafe_allow_html=True)
            if st.button("🚀  Sign Up", key="land_signup"):
                go_auth("signup"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ── TICKER + FOOTER ──────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    render_ticker()
    st.markdown(
        """
        <div style="text-align:center;margin-top:24px;font-family:'JetBrains Mono',monospace;
        font-size:11px;letter-spacing:2px;color:rgba(255,140,66,0.2);text-transform:uppercase;">
            LiteLLM Engine &nbsp;·&nbsp; RAG Pipeline &nbsp;·&nbsp;
            Firebase Auth &nbsp;·&nbsp; Twilio OTP
        </div>
        """,
        unsafe_allow_html=True,
    )
