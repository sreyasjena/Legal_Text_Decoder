"""
frontend/auth/firebase_auth.py
──────────────────────────────
All Firebase-related authentication logic.
Uses the Firebase REST API for email magic links
(works without pyrebase's missing methods).
Includes Google OAuth Sign-In via Firebase REST API.
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
# FIREBASE CONFIG  (reads from Streamlit secrets / .env)
# ─────────────────────────────────────────────────────────
FIREBASE_CRED_PATH = os.path.join(
    os.path.dirname(__file__), "..", "firebase_credentials.json"
)

def _get_secret(key: str, default: str = "") -> str:
    """Read from Streamlit secrets first, then env vars."""
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, default)

FIREBASE_CONFIG = {
    "apiKey":            _get_secret("FIREBASE_API_KEY"),
    "authDomain":        _get_secret("FIREBASE_AUTH_DOMAIN"),
    "projectId":         _get_secret("FIREBASE_PROJECT_ID"),
    "storageBucket":     _get_secret("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": _get_secret("FIREBASE_MESSAGING_SENDER_ID"),
    "appId":             _get_secret("FIREBASE_APP_ID"),
    "databaseURL":       "",
}

GOOGLE_CLIENT_ID     = _get_secret("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = _get_secret("GOOGLE_CLIENT_SECRET")
REDIRECT_URI         = _get_secret("REDIRECT_URI", "https://lexai-legal.streamlit.app/")

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

    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(FIREBASE_CRED_PATH)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Firebase Admin init failed: {e}")
            return None, None

    try:
        pb       = pyrebase.initialize_app(FIREBASE_CONFIG)
        _pb_auth = pb.auth()
    except Exception as e:
        st.error(f"Pyrebase init failed: {e}")
        return None, None

    _admin_auth = fb_auth
    return _admin_auth, _pb_auth


# ─────────────────────────────────────────────────────────
# GOOGLE SIGN-IN  (token exchange with Firebase)
# ─────────────────────────────────────────────────────────

def exchange_google_token(id_token: str):
    """
    Exchange a Google ID token (from streamlit-oauth) with Firebase.
    Returns (uid, email, display_name) on success, (None, None, None) on failure.
    """
    try:
        api_key = FIREBASE_CONFIG["apiKey"]
        fb_url  = (
            f"https://identitytoolkit.googleapis.com/v1/"
            f"accounts:signInWithIdp?key={api_key}"
        )
        fb_resp = requests.post(
            fb_url,
            json={
                "requestUri":          REDIRECT_URI,
                "postBody":            f"id_token={id_token}&providerId=google.com",
                "returnSecureToken":   True,
                "returnIdpCredential": True,
            },
            timeout=10,
        )
        fb_data = fb_resp.json()

        if "error" in fb_data:
            st.error(f"Firebase Google sign-in error: {fb_data['error'].get('message', 'Unknown')}")
            return None, None, None

        uid          = fb_data.get("localId")
        email        = fb_data.get("email")
        display_name = fb_data.get("displayName", email)

        return uid, email, display_name

    except Exception as e:
        st.error(f"Google token exchange failed: {e}")
        return None, None, None


# ─────────────────────────────────────────────────────────
# EMAIL MAGIC LINK  (via Firebase REST API)
# ─────────────────────────────────────────────────────────
def send_email_link(email: str) -> bool:
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
    try:
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        if "oobCode" in params:
            return params["oobCode"][0]
        if "link" in params:
            inner        = urlparse(params["link"][0])
            inner_params = parse_qs(inner.query)
            if "oobCode" in inner_params:
                return inner_params["oobCode"][0]
        return ""
    except Exception:
        return ""


def verify_email_link(email: str, link: str):
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
    admin_auth, _ = get_firebase()
    if not admin_auth:
        return "demo_uid"

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
