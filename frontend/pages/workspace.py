"""
frontend/pages/workspace.py
────────────────────────────
Main workspace page — document input, analysis,
pipeline visibility, and voice output.
"""

import streamlit as st

from frontend.utils.session       import go_auth, go_landing, logout
from frontend.components.ticker   import render_ticker
from frontend.components.pipeline import render_pipeline, STAGE_KEYS
from frontend.components.sidebar  import render_sidebar

try:
    from backend.llm_engine import analyze_legal_text
    from backend.audio      import text_to_speech
    from backend.extractor  import (
        extract_text_from_pdf,
        extract_text_from_docx,
        extract_text_from_image,
    )
    BACKEND_AVAILABLE = True
except Exception:
    BACKEND_AVAILABLE = False


def show_workspace():
    """Render the full workspace page."""

    # Guard: redirect to auth if not logged in
    if not st.session_state.logged_in:
        go_auth("login")
        st.rerun()

    # Faint LEXAI watermark behind content
    st.markdown('<div class="main-lexai-mark">LEXAI</div>', unsafe_allow_html=True)

    # Sidebar (returns selected language)
    language_sidebar = render_sidebar()

    # ── TOPBAR ────────────────────────────────────────────
    user_display = (st.session_state.user_email or "User")[:30]
    st.markdown(
        f"""
        <div class="topbar">
            <div style="display:flex;align-items:center;gap:14px;">
                <div class="topbar-icon">⚖️</div>
                <div>
                    <div class="topbar-brand-small">Legal Intelligence System</div>
                    <div class="topbar-brand-name">LexAI Workspace</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:14px;">
                <div class="user-badge">👤 &nbsp;{user_display}</div>
                <div class="status-pill">
                    <div class="pulse-dot"></div>AI Online
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Back + Logout row
    bk1, bk2, bk3 = st.columns([0.15, 0.7, 0.15])
    with bk1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← Home", key="ws_back_top"):
            go_landing(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with bk3:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪 Log Out", key="ws_logout_top"):
            logout(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    render_ticker()

    # ── INPUT PANELS ──────────────────────────────────────
    col_left, col_right = st.columns([1.15, 0.85], gap="large")

    with col_left:
        st.markdown(
            """
            <div class="panel">
                <div class="corner-tl"></div><div class="corner-br"></div>
                <div class="panel-title">✍️ &nbsp; Legal Text Input</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sec-label">Research Prompt</div>', unsafe_allow_html=True)
        text_input = st.text_area(
            "Legal content",
            height=240,
            placeholder="Paste your contract, NDA, policy clause, or any legal document here…",
            label_visibility="collapsed",
        )
        st.markdown(
            """
            <div class="tip-card">
                <div class="tip-label">💡 Prompt Tips</div>
                <div class="tip-text">Include the document type, jurisdiction, and any
                specific clauses you want risk-assessed for best results.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            """
            <div class="panel" style="min-height:170px;">
                <div class="corner-tl"></div><div class="corner-br"></div>
                <div class="panel-title">📂 &nbsp; Document Upload</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sec-label">Reference Document</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drop file",
            type=["txt", "pdf", "docx", "png", "jpg", "jpeg"],
            label_visibility="collapsed",
        )
        if uploaded_file:
            st.markdown(
                f"""
                <div class="file-confirm">
                    <span style="font-size:24px;">✅</span>
                    <div>
                        <div style="font-size:16px;color:var(--success);font-weight:600;">
                            {uploaded_file.name}
                        </div>
                        <div style="font-size:13px;color:var(--muted);margin-top:3px;
                        font-family:'JetBrains Mono',monospace;">
                            {round(uploaded_file.size / 1024, 1)} KB · Ready
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Language selector (visible on page)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel" style="padding:20px 24px;">
                <div class="corner-tl"></div>
                <div class="panel-title" style="font-size:19px;margin-bottom:12px;">
                    🌍 &nbsp; Output Language
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sec-label">Select Language</div>', unsafe_allow_html=True)
        language_main = st.selectbox(
            "Output language",
            ["English", "Hindi", "French", "German"],
            key="lang_main",
            label_visibility="collapsed",
        )
        st.markdown(
            f'<div class="lang-display">🌍 &nbsp; Output → {language_main}</div>',
            unsafe_allow_html=True,
        )

    language = language_main

    # ── ANALYZE BUTTON ────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    bl, bc, br = st.columns([1.2, 1, 1.2])
    with bc:
        st.markdown('<div class="analyze-btn">', unsafe_allow_html=True)
        analyze_clicked = st.button("🔍  Analyze Document", key="analyze_btn")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:18px;justify-content:center;">
            <span class="hex-badge">📜 NDA Analysis</span>
            <span class="hex-badge">⚖️ Contract Review</span>
            <span class="hex-badge">🏛️ Policy Interpretation</span>
            <span class="hex-badge">🔐 Liability Clauses</span>
            <span class="hex-badge">📋 Terms of Service</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── ANALYSIS LOGIC ────────────────────────────────────
    pipeline_ph = st.empty()

    if analyze_clicked:
        if text_input.strip() == "" and uploaded_file is None:
            st.warning("⚠️  Please provide legal text or upload a document.")

        elif not BACKEND_AVAILABLE:
            st.error("Backend modules not available. Check your backend folder.")

        else:
            final_text = ""

            # Stage 1 — Extract
            st.session_state.pipeline_stage = "extracting"
            with pipeline_ph.container():
                render_pipeline("extracting")

            if uploaded_file is not None:
                ftype = uploaded_file.name.split(".")[-1].lower()
                if   ftype == "pdf":                final_text = extract_text_from_pdf(uploaded_file)
                elif ftype == "docx":               final_text = extract_text_from_docx(uploaded_file)
                elif ftype in ("png","jpg","jpeg"): final_text = extract_text_from_image(uploaded_file)
                elif ftype == "txt":                final_text = uploaded_file.read().decode("utf-8")
            else:
                final_text = text_input

            # Stages 2-4
            for stage in ["retrieving", "augmenting", "generating"]:
                st.session_state.pipeline_stage = stage
                with pipeline_ph.container():
                    render_pipeline(stage)

            # LLM call
            with st.spinner(""):
                result = analyze_legal_text(text=final_text, language=language)
                st.session_state.result = result

            # Stage 5 — Done
            st.session_state.pipeline_stage = "done"
            with pipeline_ph.container():
                render_pipeline("done")

    elif st.session_state.pipeline_stage is not None:
        with pipeline_ph.container():
            render_pipeline(st.session_state.pipeline_stage)

    # ── RESULT DISPLAY ────────────────────────────────────
    if st.session_state.result:
        st.markdown(
            f"""
            <div class="result-panel">
                <div class="corner-tl"></div><div class="corner-br"></div>
                <div class="sec-label">Paper Viewer — Live Manuscript Output</div>
                <div class="result-heading">
                    📑 &nbsp; Analysis Result
                    <span class="hex-badge" style="margin-left:auto;font-size:12px;">Ready</span>
                </div>
                <div class="result-body">{st.session_state.result}</div>
                <div class="meta-chips">
                    <span class="meta-chip chip-orange">🌍 Language: {language}</span>
                    <span class="meta-chip chip-teal">✦ RAG Augmented</span>
                    <span class="meta-chip chip-blue">✦ AI Verified</span>
                    <span class="meta-chip chip-yellow">⚖️ Legal Intelligence</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── VOICE OUTPUT ──────────────────────────────────
        st.markdown(
            """
            <div class="audio-wrap">
                <div style="font-family:'Rajdhani',sans-serif;font-size:24px;font-weight:700;
                color:var(--teal);margin-bottom:8px;">🔊 &nbsp; Voice Output</div>
                <div style="font-size:16px;color:var(--text2);margin-bottom:20px;line-height:1.8;">
                    Generate a natural-speech audio reading of the analysis in your chosen language.
                </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="voice-btn">', unsafe_allow_html=True)
        if st.button("🎙️  Generate Voice Output", key="voice_btn"):
            if BACKEND_AVAILABLE:
                with st.spinner("Synthesizing audio…"):
                    audio_path  = text_to_speech(
                        text=st.session_state.result, language="en"
                    )
                    audio_bytes = open(audio_path, "rb").read()
                    st.audio(audio_bytes, format="audio/mp3")
                    st.success("✅  Audio generated successfully!")
            else:
                st.error("Backend not available.")
        st.markdown('</div></div>', unsafe_allow_html=True)
