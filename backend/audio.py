from gtts import gTTS
import os
import uuid

# =========================================================
# GENERATE VOICE OUTPUT
# =========================================================

def text_to_speech(text, language="en"):
    """
    Convert text into speech and save as mp3
    """

    # Create temp_audio folder if not exists
    os.makedirs("temp_audio", exist_ok=True)

    # Unique filename
    filename = f"temp_audio/audio_{uuid.uuid4()}.mp3"

    # Generate speech
    tts = gTTS(
        text=text,
        lang=language
    )

    # Save audio
    tts.save(filename)

    return filename