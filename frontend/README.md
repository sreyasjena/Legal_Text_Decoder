# ⚖️ LexAI — Legal Intelligence Platform

AI-powered multilingual legal document analyzer with RAG, Firebase Auth, pipeline transparency, and voice output.

---

## 🚀 Features

- **RAG-Augmented Analysis** — searches 12,000+ legal documents
- **Multilingual Output** — English, Hindi, French, German
- **Voice Synthesis** — reads analysis aloud
- **Real-time Pipeline** — watch every AI step live
- **Secure Auth** — Firebase email magic link + Twilio phone OTP
- **Persistent Login** — session stays active until logout

---

## 📁 Project Structure

```
Legal_Text_Decoder/
├── backend/                  # AI engine, RAG, audio, extraction
│   ├── llm_engine.py
│   ├── rag.py
│   ├── audio.py
│   ├── extractor.py
│   └── config.py
│
├── frontend/
│   ├── app.py                # Entry point — routing only
│   ├── firebase_credentials.json   # (not committed to git)
│   │
│   ├── auth/
│   │   ├── firebase_auth.py  # Firebase email magic link
│   │   └── twilio_auth.py    # Twilio SMS OTP
│   │
│   ├── pages/
│   │   ├── landing.py        # Landing page
│   │   ├── auth_page.py      # Login / Signup
│   │   └── workspace.py      # Main workspace
│   │
│   ├── components/
│   │   ├── ticker.py         # Scrolling ticker
│   │   ├── pipeline.py       # Pipeline renderer
│   │   └── sidebar.py        # Workspace sidebar
│   │
│   ├── styles/
│   │   ├── main_css.py       # All CSS
│   │   └── injector.py       # Injects CSS + SVG backgrounds
│   │
│   └── utils/
│       └── session.py        # Session state + navigation helpers
│
├── legal_kb/                 # RAG knowledge base text files
├── temp_audio/               # Generated audio files
├── .env                      # API keys (not committed)
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/Legal_Text_Decoder.git
cd Legal_Text_Decoder
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Create `.env` file

```
OPENAI_API_KEY=sk-...
FIREBASE_API_KEY=AIza...
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=...
FIREBASE_APP_ID=1:...:web:...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_VERIFY_SID=VA...
```

### 3. Add Firebase credentials

Place your `firebase_credentials.json` in the `frontend/` folder.

### 4. Run

```bash
streamlit run frontend/app.py
```

---

## 🔐 Authentication

- **Email** — Firebase passwordless magic link (user gets email, clicks link, copies URL, pastes back)
- **Phone** — Twilio Verify SMS OTP (6-digit code sent to phone)
- Session persists until explicit logout

---

## 🌍 Deployment

See deployment guide for Streamlit Community Cloud deployment.
