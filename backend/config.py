import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Supported languages
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Odia": "or"
}

# LiteLLM model name
DEFAULT_MODEL = "gpt-4o-mini"

# Debug check
print("CONFIG LOADED")
print("KEY FOUND:", OPENAI_API_KEY is not None)