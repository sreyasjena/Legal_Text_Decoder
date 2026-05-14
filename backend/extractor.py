import os
import tempfile

from PIL import Image
from PyPDF2 import PdfReader
from docx import Document

# ── Tesseract setup ──────────────────────────────────────
# On Windows (local), set the path to the Tesseract executable.
# On Linux (Streamlit Cloud), tesseract is installed via packages.txt
# and available on PATH — so we only set the path if the file exists.
_WINDOWS_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

try:
    import pytesseract
    if os.path.exists(_WINDOWS_TESSERACT):
        pytesseract.pytesseract.tesseract_cmd = _WINDOWS_TESSERACT
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


# ─────────────────────────────────────────────────────────
# PDF EXTRACTION
# ─────────────────────────────────────────────────────────
def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from a PDF file page by page."""
    try:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip() if text.strip() else "No text could be extracted from this PDF."
    except Exception as e:
        return f"Could not extract text from PDF: {e}"


# ─────────────────────────────────────────────────────────
# DOCX EXTRACTION
# ─────────────────────────────────────────────────────────
def extract_text_from_docx(uploaded_file) -> str:
    """Extract text from a Word (.docx) file."""
    try:
        doc = Document(uploaded_file)
        text = "\n".join(para.text for para in doc.paragraphs)
        return text.strip() if text.strip() else "No text could be extracted from this document."
    except Exception as e:
        return f"Could not extract text from DOCX: {e}"


# ─────────────────────────────────────────────────────────
# IMAGE EXTRACTION  (with graceful cloud fallback)
# ─────────────────────────────────────────────────────────
def extract_text_from_image(uploaded_file) -> str:
    """
    Extract text from an image using Tesseract OCR.

    Falls back gracefully if Tesseract is not installed
    (e.g. first deploy before packages.txt is picked up).
    """
    if not TESSERACT_AVAILABLE:
        return (
            "⚠️ pytesseract is not installed. "
            "Please add it to requirements.txt and redeploy."
        )

    try:
        # Write to a temp file so PIL can open it reliably
        suffix = ".png"
        if hasattr(uploaded_file, "name"):
            ext = os.path.splitext(uploaded_file.name)[-1].lower()
            if ext in (".jpg", ".jpeg", ".png"):
                suffix = ext

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name

        image = Image.open(temp_path)
        text  = pytesseract.image_to_string(image)
        os.remove(temp_path)

        return text.strip() if text.strip() else "No text found in this image."

    except pytesseract.pytesseract.TesseractNotFoundError:
        return (
            "⚠️ Tesseract OCR is not available on this server.\n\n"
            "For image files, please:\n"
            "• Convert your image to PDF and upload that instead, or\n"
            "• Copy the text from the image and paste it directly into the text box."
        )
    except Exception as e:
        return f"Could not extract text from image: {e}"


# ─────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────
def extract_text(uploaded_file) -> str:
    """
    Route the uploaded file to the correct extractor
    based on its file extension.
    """
    if not hasattr(uploaded_file, "name"):
        return "Invalid file — no filename found."

    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    elif name.endswith((".png", ".jpg", ".jpeg")):
        return extract_text_from_image(uploaded_file)
    elif name.endswith(".txt"):
        try:
            return uploaded_file.read().decode("utf-8")
        except Exception as e:
            return f"Could not read text file: {e}"
    else:
        return (
            "⚠️ Unsupported file format. "
            "Please upload a PDF, DOCX, PNG, JPG, or TXT file."
        )