"""
frontend/pages/workspace.py
────────────────────────────
Main workspace page — document input, analysis,
pipeline visibility, voice output, and document Q&A.
"""

import streamlit as st

from frontend.utils.session       import go_auth, go_landing, logout
from frontend.components.ticker   import render_ticker
from frontend.components.pipeline import render_pipeline, STAGE_KEYS
from frontend.components.sidebar  import render_sidebar

try:
    from backend.llm_engine import (
        analyze_legal_text,
        answer_document_question,
        generate_qa_suggestions,
    )
    from backend.audio      import text_to_speech
    from backend.extractor  import (
        extract_text_from_pdf,
        extract_text_from_docx,
        extract_text_from_image,
    )
    BACKEND_AVAILABLE = True
    _BACKEND_ERROR = ""
except Exception as _backend_err:
    BACKEND_AVAILABLE = False
    _BACKEND_ERROR = str(_backend_err)


def show_workspace():
    """Render the full workspace page."""

    # Guard: redirect to auth if not logged in
    if not st.session_state.logged_in:
        go_auth("login")
        st.rerun()

    # ── Session state defaults ─────────────────────────────
    if "source_label"    not in st.session_state:
        st.session_state.source_label    = None
    if "analyzed_text"   not in st.session_state:
        st.session_state.analyzed_text   = None
    if "qa_history"      not in st.session_state:
        st.session_state.qa_history      = []
    if "qa_suggestions"  not in st.session_state:
        st.session_state.qa_suggestions  = []
    if "qa_prefill"      not in st.session_state:
        st.session_state.qa_prefill      = ""

    # Faint LEXAI watermark behind content
    st.markdown('<div class="main-lexai-mark">LEXAI</div>', unsafe_allow_html=True)

    # Sidebar
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
            accept_multiple_files=False,
            label_visibility="collapsed",
            key="file_uploader",
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

        # Language selector
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

        st.session_state.result         = None
        st.session_state.pipeline_stage = None
        st.session_state.source_label   = None
        st.session_state.analyzed_text  = None
        st.session_state.qa_history     = []
        st.session_state.qa_suggestions = []
        st.session_state.qa_prefill     = ""
        pipeline_ph.empty()

        if text_input.strip() == "" and uploaded_file is None:
            st.warning("⚠️  Please provide legal text or upload a document.")

        elif not BACKEND_AVAILABLE:
            st.error(f"Backend import error: {_BACKEND_ERROR}")

        else:
            final_text = ""

            if uploaded_file is not None:
                st.session_state.source_label = uploaded_file.name
            else:
                preview = text_input.strip()[:10]
                st.session_state.source_label = f'"{preview}…"' if len(text_input.strip()) > 10 else f'"{preview}"'

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

            st.session_state.analyzed_text = final_text

            for stage in ["retrieving", "augmenting", "generating"]:
                st.session_state.pipeline_stage = stage
                with pipeline_ph.container():
                    render_pipeline(stage)

            with st.spinner(""):
                result = analyze_legal_text(text=final_text, language=language)
                st.session_state.result = result

            # Generate dynamic suggestions after analysis
            with st.spinner("Generating suggestions…"):
                st.session_state.qa_suggestions = generate_qa_suggestions(
                    document_text=final_text,
                    analysis_result=result,
                )

            st.session_state.pipeline_stage = "done"
            with pipeline_ph.container():
                render_pipeline("done")

    elif st.session_state.pipeline_stage is not None:
        with pipeline_ph.container():
            render_pipeline(st.session_state.pipeline_stage)

    # ── RESULT DISPLAY ────────────────────────────────────
    if st.session_state.result:
        source_label = st.session_state.get("source_label", "—")
        st.markdown(
            f"""
            <div class="result-panel">
                <div class="corner-tl"></div><div class="corner-br"></div>
                <div class="sec-label">Paper Viewer — Live Manuscript Output</div>
                <div class="result-heading">
                    📑 &nbsp; Analysis Result
                    <span class="hex-badge" style="margin-left:auto;font-size:12px;">Ready</span>
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:13px;
                color:var(--muted);margin-bottom:14px;padding:6px 10px;
                background:rgba(255,255,255,0.04);border-left:3px solid var(--orange);
                border-radius:4px;">
                    📄 &nbsp; Source: {source_label}
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

        # ── DOCUMENT Q&A ──────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="
                background:linear-gradient(135deg,rgba(255,140,66,0.07),rgba(56,165,255,0.05));
                border:1px solid rgba(255,140,66,0.25);
                border-radius:16px;padding:28px 32px;
                position:relative;overflow:hidden;margin-top:8px;">
                <div style="position:absolute;top:0;left:0;right:0;height:2px;
                    background:linear-gradient(90deg,var(--orange),var(--teal),var(--orange));
                    background-size:200%;animation:bannerShine 3s ease infinite;"></div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:26px;font-weight:700;
                    color:var(--orange);margin-bottom:6px;">
                    💬 &nbsp; Ask About This Document
                </div>
                <div style="font-size:15px;color:var(--text2);margin-bottom:4px;">
                    Ask any question about the clauses, risks, parties, or legal terms in this document.
                    LexAI uses RAG to retrieve relevant sections before answering.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Chat history ──────────────────────────────────
        if st.session_state.qa_history:
            for turn in st.session_state.qa_history:
                st.markdown(
                    f"""
                    <div style="display:flex;justify-content:flex-end;margin:12px 0 4px;">
                        <div style="
                            background:rgba(255,140,66,0.12);
                            border:1px solid rgba(255,140,66,0.3);
                            border-radius:14px 14px 2px 14px;
                            padding:12px 18px;max-width:75%;
                            font-size:15px;color:var(--text);line-height:1.6;">
                            🧑 &nbsp; {turn['question']}
                        </div>
                    </div>
                    <div style="display:flex;justify-content:flex-start;margin:4px 0 12px;">
                        <div style="
                            background:rgba(0,229,160,0.07);
                            border:1px solid rgba(0,229,160,0.2);
                            border-radius:14px 14px 14px 2px;
                            padding:12px 18px;max-width:80%;
                            font-size:15px;color:var(--text);line-height:1.7;">
                            ⚖️ &nbsp; {turn['answer']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # ── Dynamic suggestion bubbles ────────────────────
        suggestions = st.session_state.get("qa_suggestions", [])
        if suggestions:
            # Inject custom CSS for suggestion buttons
            suggestion_css = """
<style>
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
""" + "".join([
    f"""
div[data-testid="column"]:nth-child({i+1}) button {{
    background: linear-gradient(135deg, rgba(255,140,66,0.08), rgba(56,165,255,0.06)) !important;
    border: 1px solid rgba(255,140,66,{0.2 + i*0.05:.2f}) !important;
    border-radius: 20px !important;
    color: var(--text, #e8e8e8) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.5px !important;
    padding: 8px 14px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    animation: suggestionPulse {1.5 + i*0.2:.1f}s ease-in-out infinite alternate !important;
    box-shadow: 0 0 8px rgba(255,140,66,{0.1 + i*0.03:.2f}) !important;
    white-space: normal !important;
    height: auto !important;
    min-height: 42px !important;
    line-height: 1.4 !important;
    text-transform: uppercase !important;
}}
div[data-testid="column"]:nth-child({i+1}) button:hover {{
    background: linear-gradient(135deg, rgba(255,140,66,0.2), rgba(56,165,255,0.15)) !important;
    border-color: rgba(255,140,66,0.7) !important;
    box-shadow: 0 0 16px rgba(255,140,66,0.35), 0 0 32px rgba(255,140,66,0.15) !important;
    transform: translateY(-2px) !important;
    color: #ff8c42 !important;
}}
"""
    for i in range(len(suggestions))
]) + """
@keyframes suggestionPulse {
    0% { box-shadow: 0 0 6px rgba(255,140,66,0.1); border-color: rgba(255,140,66,0.2); }
    100% { box-shadow: 0 0 14px rgba(255,140,66,0.3); border-color: rgba(255,140,66,0.5); }
}
</style>
"""
            st.markdown(suggestion_css, unsafe_allow_html=True)
            st.markdown(
                """
                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                color:rgba(255,140,66,0.6);letter-spacing:2px;margin:18px 0 10px;
                display:flex;align-items:center;gap:8px;">
                    <span style="display:inline-block;width:20px;height:1px;
                    background:rgba(255,140,66,0.4);"></span>
                    💡 SUGGESTED QUESTIONS
                    <span style="display:inline-block;flex:1;height:1px;
                    background:rgba(255,140,66,0.2);"></span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            cols = st.columns(len(suggestions))
            for i, (col, suggestion) in enumerate(zip(cols, suggestions)):
                with col:
                    if st.button(
                        suggestion,
                        key=f"suggestion_{i}",
                        use_container_width=True,
                    ):
                        st.session_state.qa_prefill = suggestion
                        st.rerun()

        # ── Q&A Input ─────────────────────────────────────
        # If a suggestion was clicked, update the widget state key directly
        if st.session_state.qa_prefill:
            st.session_state["qa_input"] = st.session_state.qa_prefill
            st.session_state.qa_prefill  = ""

        st.markdown("<br>", unsafe_allow_html=True)
        qa_col1, qa_col2 = st.columns([5, 1])

        with qa_col1:
            user_question = st.text_input(
                "Ask a question",
                placeholder="e.g. What is the deposit amount? What are my risks?",
                key="qa_input",
                label_visibility="collapsed",
            )

        with qa_col2:
            ask_clicked = st.button("Ask ➤", key="qa_ask_btn", use_container_width=True)

        # ── Handle Q&A submission ─────────────────────────
        if ask_clicked and user_question.strip():
            st.session_state["qa_input"] = ""

            if not BACKEND_AVAILABLE:
                st.error("Backend not available.")
            elif not st.session_state.analyzed_text:
                st.warning("⚠️ No document text available. Please analyze a document first.")
            else:
                with st.spinner("🔍 Searching document and retrieving answer…"):
                    answer = answer_document_question(
                        question=user_question.strip(),
                        document_text=st.session_state.analyzed_text,
                        language=language,
                        chat_history=st.session_state.qa_history,
                    )

                st.session_state.qa_history.append({
                    "question": user_question.strip(),
                    "answer":   answer,
                })
                st.rerun()

        # ── Clear chat ────────────────────────────────────
        if st.session_state.qa_history:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Clear Chat", key="qa_clear"):
                st.session_state.qa_history  = []
                st.session_state.qa_prefill  = ""
                st.rerun()
