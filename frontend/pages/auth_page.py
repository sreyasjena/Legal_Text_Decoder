"""
frontend/pages/auth_page.py
────────────────────────────
Login and Sign-up page.
Two-column layout: branding panel (left) + form card (right).
Supports Google Sign-In, email magic link, and phone SMS OTP.
"""

import streamlit as st

from frontend.utils.session import go_landing, go_workspace
from frontend.auth.firebase_auth import (
    send_email_link,
    verify_email_link,
    firebase_create_or_get_user,
    get_google_auth_url,
    exchange_google_code,
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

# ── Security card shown at top of form column ────────────
SECURITY_CARD = """
<div style="
    background:linear-gradient(135deg,rgba(0,229,160,0.07),rgba(56,165,255,0.06));
    border:1px solid rgba(0,229,160,0.22);
    border-radius:16px;padding:18px 22px;margin-bottom:18px;
    display:flex;align-items:center;gap:16px;
    position:relative;overflow:hidden;">
    <div style="position:absolute;top:0;left:0;right:0;height:2px;
        background:linear-gradient(90deg,var(--success),var(--cyan),var(--success));
        background-size:200%;animation:bannerShine 3s ease infinite;"></div>
    <div style="width:48px;height:48px;border-radius:12px;flex-shrink:0;
        background:linear-gradient(135deg,rgba(0,229,160,0.15),rgba(56,165,255,0.1));
        border:1px solid rgba(0,229,160,0.3);
        display:flex;align-items:center;justify-content:center;font-size:24px;">
        🔐
    </div>
    <div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
            letter-spacing:2.5px;text-transform:uppercase;
            color:var(--success);margin-bottom:5px;display:flex;align-items:center;gap:6px;">
            <span style="width:7px;height:7px;background:var(--success);
            border-radius:50%;display:inline-block;
            box-shadow:0 0 8px var(--success);"></span>
            Secure Connection Active
        </div>
        <div style="font-size:13px;color:var(--text2);line-height:1.6;">
            All data is <strong style="color:var(--text);">encrypted end-to-end</strong>.
            No passwords stored ever. Protected by
            <strong style="color:var(--orange);">Firebase Auth</strong> +
            <strong style="color:var(--blue);">Twilio OTP</strong>.
        </div>
    </div>
</div>
"""

# ── Google Sign-In button HTML ────────────────────────────
def _google_button(auth_url: str) -> str:
    return f"""
<a href="{auth_url}" target="_self" style="text-decoration:none;">
    <div style="
        display:flex;align-items:center;justify-content:center;gap:12px;
        background:#fff;color:#3c4043;
        border:1px solid #dadce0;border-radius:10px;
        padding:12px 20px;cursor:pointer;width:100%;
        font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;
        letter-spacing:0.5px;margin-bottom:6px;
        box-shadow:0 1px 6px rgba(0,0,0,0.2);
        transition:box-shadow 0.2s ease;">
        <svg width="20" height="20" viewBox="0 0 48 48">
            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
            <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
            <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
            <path fill="none" d="M0 0h48v48H0z"/>
        </svg>
        Continue with Google
    </div>
</a>
<div style="display:flex;align-items:center;gap:10px;margin:14px 0 10px;">
    <div style="flex:1;height:1px;background:rgba(255,255,255,0.1);"></div>
    <span style="font-family:'JetBrains Mono',monospace;font-size:11px;
    color:var(--muted);letter-spacing:1px;">OR</span>
    <div style="flex:1;height:1px;background:rgba(255,255,255,0.1);"></div>
</div>
"""


# ─────────────────────────────────────────────────────────
# GOOGLE OAUTH CALLBACK HANDLER
# ─────────────────────────────────────────────────────────

def _handle_google_callback():
    """
    Check URL query params for Google OAuth callback code.
    If found, exchange it for Firebase credentials and log the user in.
    Returns True if login was completed, False otherwise.
    """
    try:
        params = st.query_params
        code   = params.get("code", None)

        if not code:
            return False

        # Clear the code from URL immediately to prevent re-use on refresh
        st.query_params.clear()

        with st.spinner("🔄 Completing Google Sign-In…"):
            uid, email, display_name = exchange_google_code(code)

        if uid and email:
            st.session_state.logged_in  = True
            st.session_state.user_uid   = uid
            st.session_state.user_email = email
            st.session_state.otp_sent   = False
            go_workspace()
            st.rerun()
            return True
        else:
            st.error("❌ Google Sign-In failed. Please try again.")
            return False

    except Exception as e:
        st.error(f"Google callback error: {e}")
        return False


# ─────────────────────────────────────────────────────────
# SHARED FORM HELPERS
# ─────────────────────────────────────────────────────────

def _email_form(key_prefix: str, button_label: str, button_class: str):
    """Shared email OTP form for both Login and Signup tabs."""
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
            f"""<div class="success-box">
                ✅ Link sent to <strong>{st.session_state.pending_email}</strong><br>
                Check inbox → click link → copy full URL → paste below.
            </div>""",
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
    """Shared phone OTP form for both Login and Signup tabs."""
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

    # ── Handle Google OAuth callback first ───────────────
    # If ?code=... is in the URL, complete the sign-in and exit early
    if _handle_google_callback():
        return

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
                        <span class="auth-feat-icon">🔊</span>
                        <div class="auth-feat-text">
                            <strong>Voice synthesis</strong> — AI reads your legal
                            analysis aloud in your chosen language, hands-free.
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

    # ── RIGHT: security card + form card ─────────────────
    with right_col:

        # ── Security badge card ───────────────────────────
        st.markdown(SECURITY_CARD, unsafe_allow_html=True)

        # ── Main form card ────────────────────────────────
        st.markdown(
            '<div class="auth-form-card"><div class="fc-tl"></div><div class="fc-br"></div>',
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(["  🔑  Log In  ", "  🚀  Sign Up  "])

        # ── LOG IN TAB ───────────────────────────────────
        with tab1:
            st.markdown(
                '<div class="auth-form-title">Welcome back</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="auth-form-subtitle">'
                'Choose your login method — no password needed.</div>',
                unsafe_allow_html=True,
            )

            # ── Google Sign-In button ─────────────────────
            google_url = get_google_auth_url()
            st.markdown(_google_button(google_url), unsafe_allow_html=True)

            _method_selector("li")
            if st.session_state.auth_method == "email":
                _email_form("li", "Send Login Link", "btn-otp")
            else:
                _phone_form("li", "Send OTP via SMS", "btn-otp")

        # ── SIGN UP TAB ──────────────────────────────────
        with tab2:
            st.markdown(
                '<div class="auth-form-title">Create account</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="auth-form-subtitle">'
                'No password required. Verify with email or phone.</div>',
                unsafe_allow_html=True,
            )

            # ── Google Sign-In button ─────────────────────
            st.markdown(_google_button(google_url), unsafe_allow_html=True)

            _method_selector("su")
            if st.session_state.auth_method == "email":
                _email_form("su", "🚀  Send Signup Link", "btn-signup")
            else:
                _phone_form("su", "🚀  Send OTP to Register", "btn-signup")

        st.markdown('</div>', unsafe_allow_html=True)  # close auth-form-card
