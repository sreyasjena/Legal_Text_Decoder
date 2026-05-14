"""
frontend/pages/auth_page.py
────────────────────────────
Login and Sign-up page.
Two-column layout: branding panel (left) + form card (right).
Supports email magic link and phone SMS OTP.
"""

import streamlit as st

from frontend.utils.session  import go_landing, go_workspace, logout
from frontend.auth.firebase_auth import (
    send_email_link,
    verify_email_link,
    firebase_create_or_get_user,
)
from frontend.auth.twilio_auth import send_phone_otp, verify_phone_otp

# ── Instruction block shown for email login ──────────────
EMAIL_INSTRUCTIONS = """
<div class="instr-box">
    <strong style="color:var(--orange);">📧 How Email Login Works:</strong>
    <ol>
        <li>Enter your email and click <strong>Send Login Link</strong></li>
        <li>Firebase sends a magic link to your inbox — check your email</li>
        <li>Click the link in the email — it opens a browser page</li>
        <li>Copy the <strong>full URL</strong> from your browser address bar</li>
        <li>Paste that URL back here and click <strong>Verify</strong></li>
    </ol>
</div>
"""


def _email_form(key_prefix: str, button_label: str, button_class: str):
    """
    Shared email OTP form used by both Log In and Sign Up tabs.
    key_prefix   : unique prefix for widget keys ('li' or 'su')
    button_label : text on the send button
    button_class : CSS class for the send button ('btn-otp' or 'btn-signup')
    """
    st.markdown(EMAIL_INSTRUCTIONS, unsafe_allow_html=True)
    st.markdown('<span class="form-label">📧 Email Address</span>', unsafe_allow_html=True)
    email = st.text_input(
        "Email",
        placeholder="you@example.com",
        key=f"{key_prefix}_email",
        label_visibility="collapsed",
    )

    if not st.session_state.otp_sent:
        st.markdown(f'<div class="{button_class}">', unsafe_allow_html=True)
        if st.button(f"{button_label} →", key=f"{key_prefix}_send_email"):
            if email.strip() and "@" in email:
                with st.spinner("Sending secure link…"):
                    ok = send_email_link(email.strip())
                if ok:
                    st.session_state.otp_sent     = True
                    st.session_state.pending_email = email.strip()
                    st.rerun()
            else:
                st.warning("Enter a valid email address.")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown(
            f"""
            <div class="success-box">
                ✅ Link sent to <strong>{st.session_state.pending_email}</strong><br>
                Check inbox → click link → copy full URL → paste below.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<span class="form-label">🔗 Paste the Full URL from Browser</span>',
            unsafe_allow_html=True,
        )
        magic = st.text_input(
            "Magic link URL",
            placeholder="https://lexai-74320.firebaseapp.com/__/auth/action?apiKey=…",
            key=f"{key_prefix}_magic",
            label_visibility="collapsed",
        )
        st.markdown('<div class="btn-verify">', unsafe_allow_html=True)
        if st.button("✅  Verify & Enter Workspace", key=f"{key_prefix}_verify_email"):
            if magic.strip():
                with st.spinner("Verifying link…"):
                    uid, vemail = verify_email_link(
                        st.session_state.pending_email, magic.strip()
                    )
                if uid:
                    st.session_state.logged_in  = True
                    st.session_state.user_uid   = uid
                    st.session_state.user_email = vemail
                    st.session_state.otp_sent   = False
                    go_workspace()
                    st.rerun()
            else:
                st.warning("Paste the complete URL.")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("↩ Resend / change email", key=f"{key_prefix}_resend_email"):
            st.session_state.otp_sent = False
            st.rerun()


def _phone_form(key_prefix: str, button_label: str, button_class: str):
    """
    Shared phone OTP form used by both Log In and Sign Up tabs.
    """
    st.markdown(
        '<span class="form-label">📱 Phone Number (with country code)</span>',
        unsafe_allow_html=True,
    )
    phone = st.text_input(
        "Phone",
        placeholder="+91 98765 43210",
        key=f"{key_prefix}_phone",
        label_visibility="collapsed",
    )
    st.markdown(
        '<div class="info-box">ℹ️ Include country code: '
        '<strong>+91</strong> India &nbsp;·&nbsp; '
        '<strong>+1</strong> US &nbsp;·&nbsp; '
        '<strong>+44</strong> UK</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.otp_sent:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="{button_class}">', unsafe_allow_html=True)
        if st.button(f"{button_label} →", key=f"{key_prefix}_send_phone"):
            p = phone.strip().replace(" ", "")
            if p.startswith("+") and len(p) >= 8:
                with st.spinner("Sending OTP…"):
                    ok = send_phone_otp(p)
                if ok:
                    st.session_state.otp_sent      = True
                    st.session_state.pending_phone = p
                    st.rerun()
            else:
                st.warning("Enter a valid phone number with country code.")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown(
            f'<div class="success-box">📱 OTP sent to '
            f'<strong>{st.session_state.pending_phone}</strong></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<span class="form-label">🔢 6-Digit OTP Code</span>',
            unsafe_allow_html=True,
        )
        otp = st.text_input(
            "OTP",
            placeholder="123456",
            max_chars=6,
            key=f"{key_prefix}_otp",
            label_visibility="collapsed",
        )
        st.markdown('<div class="btn-verify">', unsafe_allow_html=True)
        if st.button("✅  Verify & Enter", key=f"{key_prefix}_verify_phone"):
            if len(otp.strip()) == 6:
                with st.spinner("Verifying OTP…"):
                    ok = verify_phone_otp(st.session_state.pending_phone, otp.strip())
                if ok:
                    uid = firebase_create_or_get_user(
                        phone=st.session_state.pending_phone
                    )
                    if uid:
                        st.session_state.logged_in  = True
                        st.session_state.user_uid   = uid
                        st.session_state.user_email = st.session_state.pending_phone
                        st.session_state.otp_sent   = False
                        go_workspace()
                        st.rerun()
                else:
                    st.error("❌ Invalid OTP. Please try again.")
            else:
                st.warning("Enter the complete 6-digit OTP.")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("↩ Resend / change number", key=f"{key_prefix}_resend_phone"):
            st.session_state.otp_sent = False
            st.rerun()


def _method_selector(key_prefix: str):
    """Render Email / Phone method toggle buttons and visual chips."""
    mc1, mc2 = st.columns(2)
    with mc1:
        if st.button("📧  Email OTP", key=f"{key_prefix}_method_email"):
            st.session_state.auth_method = "email"
            st.session_state.otp_sent    = False
            st.rerun()
    with mc2:
        if st.button("📱  Phone OTP", key=f"{key_prefix}_method_phone"):
            st.session_state.auth_method = "phone"
            st.session_state.otp_sent    = False
            st.rerun()

    active = st.session_state.auth_method
    st.markdown(
        f"""
        <div class="method-row">
            <div class="method-chip {'active' if active == 'email' else ''}">
                📧 &nbsp; Email Link
            </div>
            <div class="method-chip {'active' if active == 'phone' else ''}">
                📱 &nbsp; SMS Code
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────
# PUBLIC FUNCTION
# ─────────────────────────────────────────────────────────
def show_auth():
    """Render the full auth page (login + signup)."""

    # Already logged in → skip to workspace
    if st.session_state.logged_in:
        go_workspace()
        st.rerun()

    # Back button
    b1, b2 = st.columns([0.14, 0.86])
    with b1:
        st.markdown('<div class="back-btn" style="margin-top:22px;">', unsafe_allow_html=True)
        if st.button("← Home", key="auth_back"):
            go_landing()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Two-column layout
    left_col, div_col, right_col = st.columns([1, 0.04, 1.1])

    # ── LEFT: branding panel ──────────────────────────────
    with left_col:
        st.markdown(
            """
            <div class="auth-brand-panel">
                <span class="auth-brand-logo">LEXAI</span>
                <div class="auth-brand-tagline">
                    ⚖️ &nbsp; Secure Legal Intelligence Platform
                </div>
                <div class="auth-brand-desc">
                    Join thousands of legal professionals who trust LexAI to decode
                    complex contracts, NDAs, and legal documents in seconds —
                    powered by RAG and multilingual AI.
                </div>
                <div class="auth-feat-list">
                    <div class="auth-feat-item">
                        <span class="auth-feat-icon">🔐</span>
                        <div class="auth-feat-text">
                            <strong>Zero passwords</strong> — login with a secure
                            one-time code sent to your email or phone.
                        </div>
                    </div>
                    <div class="auth-feat-item">
                        <span class="auth-feat-icon">🧠</span>
                        <div class="auth-feat-text">
                            <strong>RAG-powered</strong> analysis from 12,000+
                            curated legal documents and statutes.
                        </div>
                    </div>
                    <div class="auth-feat-item">
                        <span class="auth-feat-icon">🌍</span>
                        <div class="auth-feat-text">
                            <strong>Multilingual output</strong> — English, Hindi,
                            French, and German supported.
                        </div>
                    </div>
                    <div class="auth-feat-item">
                        <span class="auth-feat-icon">💾</span>
                        <div class="auth-feat-text">
                            <strong>Session persists</strong> — come back to the
                            home page anytime without logging in again.
                        </div>
                    </div>
                </div>
                <div class="trust-row">
                    <div class="trust-badge"><span>🔒</span> End-to-end secure</div>
                    <div class="trust-badge"><span>⚡</span> Firebase Auth</div>
                    <div class="trust-badge"><span>🛡️</span> GDPR Ready</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with div_col:
        st.markdown(
            '<div class="auth-divider-vert" style="min-height:600px;"></div>',
            unsafe_allow_html=True,
        )

    # ── RIGHT: form card ──────────────────────────────────
    with right_col:
        st.markdown(
            '<div class="auth-form-card"><div class="fc-tl"></div><div class="fc-br"></div>',
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(["  🔑  Log In  ", "  🚀  Sign Up  "])

        # LOG IN
        with tab1:
            st.markdown(
                '<div class="auth-form-title">Welcome back</div>', unsafe_allow_html=True
            )
            st.markdown(
                '<div class="auth-form-subtitle">'
                'Choose your login method — no password needed.</div>',
                unsafe_allow_html=True,
            )
            _method_selector("li")
            if st.session_state.auth_method == "email":
                _email_form("li", "Send Login Link", "btn-otp")
            else:
                _phone_form("li", "Send OTP via SMS", "btn-otp")

        # SIGN UP
        with tab2:
            st.markdown(
                '<div class="auth-form-title">Create account</div>', unsafe_allow_html=True
            )
            st.markdown(
                '<div class="auth-form-subtitle">'
                'No password required. Verify with email or phone.</div>',
                unsafe_allow_html=True,
            )
            _method_selector("su")
            if st.session_state.auth_method == "email":
                _email_form("su", "🚀  Send Signup Link", "btn-signup")
            else:
                _phone_form("su", "🚀  Send OTP to Register", "btn-signup")

        st.markdown('</div>', unsafe_allow_html=True)  # close auth-form-card
