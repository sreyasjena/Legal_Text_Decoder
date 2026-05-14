"""
frontend/components/pipeline.py
────────────────────────────────
Real-time AI pipeline visibility component.
Renders 5 stage cards using st.columns to avoid
HTML escaping issues with nested markdown.
"""

import streamlit as st

STAGES = [
    ("📥", "Extract",  "Reading & parsing document"),
    ("🔍", "Retrieve", "Querying legal knowledge base"),
    ("🧩", "Augment",  "Building context-enriched prompt"),
    ("🤖", "Generate", "LLM producing analysis"),
    ("✅", "Finalise", "Formatting & delivering result"),
]

STAGE_KEYS = [
    "extracting", "retrieving", "augmenting", "generating", "done"
]

STAGE_PROGRESS = {
    None:          0,
    "extracting":  15,
    "retrieving":  35,
    "augmenting":  55,
    "generating":  78,
    "done":        100,
}

STAGE_LOGS = {
    "extracting": "Parsing document structure and extracting raw text…",
    "retrieving": "Querying vector store — searching 12,400 legal precedents…",
    "augmenting": "Injecting retrieved context into prompt template…",
    "generating": "Running LLM inference — generating structured legal analysis…",
    "done":       "Analysis complete. Rendering output.",
}


def render_pipeline(current_stage: str):
    """
    Render the animated pipeline panel for the given stage.
    current_stage must be one of STAGE_KEYS or None.
    """
    progress   = STAGE_PROGRESS.get(current_stage, 0)
    active_idx = (
        STAGE_KEYS.index(current_stage)
        if current_stage in STAGE_KEYS else -1
    )
    log_text = STAGE_LOGS.get(current_stage, "")

    # Header
    st.markdown(
        """
        <div class="pipeline-outer">
            <div class="corner-tl"></div><div class="corner-br"></div>
            <div class="pipe-header-label">⬡ &nbsp; Agent Workflow</div>
            <div class="pipe-header-title">Real-time Pipeline Visibility</div>
        """,
        unsafe_allow_html=True,
    )

    # Stage cards — rendered in st.columns to avoid HTML escaping
    cols = st.columns(5)
    for i, (icon, name, desc) in enumerate(STAGES):
        if i < active_idx:
            cls   = "done"
            badge = '<span class="pstage-badge bd-done">✓ Completed</span>'
        elif i == active_idx:
            cls   = "active"
            badge = '<span class="pstage-badge bd-active">⬤ Running…</span>'
        else:
            cls   = "queued"
            badge = '<span class="pstage-badge bd-queued">Queue</span>'

        with cols[i]:
            st.markdown(
                f"""
                <div class="pstage {cls}">
                    <div class="pstage-icon">{icon}</div>
                    <div class="pstage-name">{name}</div>
                    <div class="pstage-desc">{desc}</div>
                    {badge}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Progress bar + live log
    st.markdown(
        f"""
        <div class="prog-wrap">
            <div class="prog-fill" style="width:{progress}%;"></div>
        </div>
        <div class="live-log">
            <span>{log_text}</span>
            <span class="blink-cursor"></span>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
