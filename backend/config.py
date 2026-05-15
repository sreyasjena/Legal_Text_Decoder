import os
from dotenv import load_dotenv

# Load environment variables from .env (local development)
load_dotenv()


def _get_secret(key: str, default: str = "") -> str:
    """Read from Streamlit secrets first, then env vars."""
    try:
        import streamlit as st
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)


# OpenAI API Key
OPENAI_API_KEY = _get_secret("OPENAI_API_KEY")

# Google OAuth credentials
GOOGLE_CLIENT_ID     = _get_secret("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = _get_secret("GOOGLE_CLIENT_SECRET")
REDIRECT_URI         = _get_secret("REDIRECT_URI", "https://lexai-legal.streamlit.app/")

# Supported languages
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Hindi":   "hi",
    "Telugu":  "te",
    "Odia":    "or"
}

# LiteLLM model name
DEFAULT_MODEL = "gpt-4o-mini"
