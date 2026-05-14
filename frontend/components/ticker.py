"""
frontend/components/ticker.py
──────────────────────────────
Scrolling news-ticker component shown on landing
and workspace pages.
"""

import streamlit as st

TICKER_ITEMS = [
    ("blue",   "⚖️  RAG-Augmented Legal Analysis"),
    ("orange", "🔊  Multilingual Voice Output"),
    ("teal",   "🌍  4 Language Support"),
    ("yellow", "🔬  Real-time Pipeline Visibility"),
    ("blue",   "📄  Multi-format Document Parsing"),
    ("orange", "🧠  LiteLLM Inference Engine"),
    ("teal",   "📚  12,000+ Legal Documents in KB"),
    ("yellow", "🔐  Secure Email & Phone OTP Login"),
    ("blue",   "✅  Firebase Auth Powered"),
    ("orange", "🛡️  End-to-End Encryption"),
]


def render_ticker():
    """Render the horizontal scrolling ticker tape."""
    inner = "".join(
        f'<div class="ticker-item t-{color}">'
        f'<span class="ticker-dot" style="background:var(--{color});'
        f'box-shadow:0 0 8px var(--{color});"></span>{text}</div>'
        for color, text in TICKER_ITEMS * 2   # duplicate for seamless loop
    )
    st.markdown(
        f'<div class="ticker-wrap"><div class="ticker-inner">{inner}</div></div>',
        unsafe_allow_html=True,
    )
