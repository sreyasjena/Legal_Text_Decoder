"""
frontend/auth/firebase_auth.py
──────────────────────────────
All Firebase-related authentication logic.
Uses the Firebase REST API for email magic links
(works without pyrebase's missing methods).
"""

import os
import requests
from urllib.parse import urlparse, parse_qs

import streamlit as st

# ── Optional Firebase imports ──
try:
    import firebase_admin
    from firebase_admin import credentials, auth as fb_auth
    import pyrebase
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

# ─────────────────────────────────────────────────────────
# FIREBASE CONFIG  (reads from .env)
# ─────────────────────────────────────────────────────────
FIREBASE_CRED_PATH = os.path.join(
    os.path.dirname(__file__), "..", "firebase_credentials.json"
)

FIREBASE_CONFIG = {
    "apiKey":            os.environ.get("FIREBASE_API_KEY", ""),
    "authDomain":        os.environ.get("FIREBASE_AUTH_DOMAIN", ""),
    "projectId":         os.environ.get("FIREBASE_PROJECT_ID", ""),
    "storageBucket":     os.environ.get("FIREBASE_STORAGE_BUCKET", ""),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID", ""),
    "appId":             os.environ.get("FIREBASE_APP_ID", ""),
    "databaseURL":       "",
}

# ─────────────────────────────────────────────────────────
# INITIALISATION  (called once per process)
# ─────────────────────────────────────────────────────────
_admin_auth = None
_pb_auth    = None

def get_firebase():
    """Return (admin_auth, pb_auth) — initialises on first call."""
    global _admin_auth, _pb_auth
    if _admin_auth is not None:
        return _admin_auth, _pb_auth

    if not FIREBASE_AVAILABLE:
        return None, None

    # Admin SDK
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(FIREBASE_CRED_PATH)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Firebase Admin init failed: {e}")
            return None, None

    # Pyrebase client
    try:
        pb       = pyrebase.initialize_app(FIREBASE_CONFIG)
        _pb_auth = pb.auth()
    except Exception as e:
        st.error(f"Pyrebase init failed: {e}")
        return None, None

    _admin_auth = fb_auth
    return _admin_auth, _pb_auth


# ─────────────────────────────────────────────────────────
# EMAIL MAGIC LINK  (via Firebase REST API)
# ─────────────────────────────────────────────────────────
def send_email_link(email: str) -> bool:
    """
    Send a Firebase passwordless sign-in link to the given email.
    Uses the Firebase REST API directly — avoids pyrebase method gaps.
    Returns True on success, False on failure.
    """
    try:
        api_key = FIREBASE_CONFIG["apiKey"]
        url     = (
            f"https://identitytoolkit.googleapis.com/v1/"
            f"accounts:sendOobCode?key={api_key}"
        )
        payload = {
            "requestType":        "EMAIL_SIGNIN",
            "email":              email,
            "continueUrl":        "https://lexai-legal.streamlit.app/",
            "canHandleCodeInApp": True,
        }
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()

        if "error" in data:
            msg = data["error"].get("message", "Unknown error")
            if msg == "OPERATION_NOT_ALLOWED":
                st.error(
                    "❌ Email link sign-in is not enabled in Firebase.\n"
                    "Go to Firebase → Authentication → Sign-in method → "
                    "Email/Password → enable 'Email link (passwordless)'."
                )
            else:
                st.error(f"Firebase error: {msg}")
            return False
        return True

    except Exception as e:
        st.error(f"Could not send email link: {e}")
        return False


def _extract_oob_code(link: str) -> str:
    """Extract the oobCode query parameter from a Firebase magic link URL."""
    try:
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        if "oobCode" in params:
            return params["oobCode"][0]
        # Sometimes nested inside a 'link' parameter
        if "link" in params:
            inner        = urlparse(params["link"][0])
            inner_params = parse_qs(inner.query)
            if "oobCode" in inner_params:
                return inner_params["oobCode"][0]
        return ""
    except Exception:
        return ""


def verify_email_link(email: str, link: str):
    """
    Verify a Firebase magic link URL.
    Returns (uid, email) on success, (None, None) on failure.
    """
    try:
        oob_code = _extract_oob_code(link)
        if not oob_code:
            st.error(
                "Could not find the verification code in the link. "
                "Please copy the full URL from your browser address bar."
            )
            return None, None

        api_key = FIREBASE_CONFIG["apiKey"]
        url     = (
            f"https://identitytoolkit.googleapis.com/v1/"
            f"accounts:signInWithEmailLink?key={api_key}"
        )
        resp = requests.post(
            url,
            json={"email": email, "oobCode": oob_code},
            timeout=10,
        )
        data = resp.json()

        if "error" in data:
            st.error(
                f"Verification failed: {data['error'].get('message', 'Unknown error')}"
            )
            return None, None

        return data.get("localId"), data.get("email")

    except Exception as e:
        st.error(f"Verification error: {e}")
        return None, None


# ─────────────────────────────────────────────────────────
# USER MANAGEMENT  (Firebase Admin SDK)
# ─────────────────────────────────────────────────────────
def firebase_create_or_get_user(email: str = None, phone: str = None):
    """
    Create a new Firebase user or fetch an existing one.
    Returns the user's uid string, or None on failure.
    """
    admin_auth, _ = get_firebase()
    if not admin_auth:
        return "demo_uid"   # graceful fallback when Firebase not configured

    try:
        if email:
            try:    user = fb_auth.get_user_by_email(email)
            except: user = fb_auth.create_user(email=email)
            return user.uid

        if phone:
            try:    user = fb_auth.get_user_by_phone_number(phone)
            except: user = fb_auth.create_user(phone_number=phone)
            return user.uid

    except Exception as e:
        st.error(f"Firebase user error: {e}")
        return None
