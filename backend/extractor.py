import os
import tempfile

from PIL import Image
from PyPDF2 import PdfReader
from docx import Document

# ── Tesseract setup ──────────────────────────────────────
_WINDOWS_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

try:
    import pytesseract
    if os.path.exists(_WINDOWS_TESSERACT):
        pytesseract.pytesseract.tesseract_cmd = _WINDOWS_TESSERACT
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# ── pdf2image for scanned PDF OCR ────────────────────────
try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


# ─────────────────────────────────────────────────────────
# PDF EXTRACTION  (digital text + OCR fallback for scanned)
# ─────────────────────────────────────────────────────────
def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract text from a PDF file.
    - First tries PyPDF2 for digital PDFs (fast).
    - If little/no text is found, falls back to Tesseract OCR
      via pdf2image (handles scanned/image-based PDFs).
    """
    try:
        # Read file bytes once so we can reuse for OCR if needed
        file_bytes = uploaded_file.read()

        # ── Step 1: Try digital text extraction ──────────
        from io import BytesIO
        pdf_reader = PdfReader(BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        text = text.strip()

        # If we got meaningful text (>100 chars), return it
        if len(text) > 100:
            return text

        # ── Step 2: OCR fallback for scanned PDFs ────────
        if PDF2IMAGE_AVAILABLE and TESSERACT_AVAILABLE:
            return _ocr_pdf_bytes(file_bytes)
        elif not PDF2IMAGE_AVAILABLE:
            return (
                "⚠️ This appears to be a scanned PDF. "
                "pdf2image is not installed — add it to requirements.txt.\n\n"
                "Tip: Copy the text from the PDF and paste it directly into the text box."
            )
        else:
            return (
                "⚠️ This appears to be a scanned PDF. "
                "Tesseract OCR is not available.\n\n"
                "Tip: Copy the text from the PDF and paste it directly into the text box."
            )

    except Exception as e:
        return f"Could not extract text from PDF: {e}"


def _ocr_pdf_bytes(file_bytes: bytes) -> str:
    """
    Convert PDF pages to images and run Tesseract OCR on each page.
    Returns combined OCR text from all pages.
    """
    try:
        pages = convert_from_bytes(file_bytes, dpi=200)
        ocr_text = ""
        for i, page_image in enumerate(pages):
            page_text = pytesseract.image_to_string(page_image, lang="eng")
            if page_text.strip():
                ocr_text += f"\n--- Page {i+1} ---\n{page_text}"

        result = ocr_text.strip()
        return result if result else "No text could be extracted from this scanned PDF."

    except pytesseract.pytesseract.TesseractNotFoundError:
        return (
            "⚠️ Tesseract OCR is not available on this server.\n\n"
            "Tip: Copy the text from the PDF and paste it directly into the text box."
        )
    except Exception as e:
        return f"OCR extraction failed: {e}"


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
    Falls back gracefully if Tesseract is not installed.
    """
    if not TESSERACT_AVAILABLE:
        return (
            "⚠️ pytesseract is not installed. "
            "Please add it to requirements.txt and redeploy."
        )

    try:
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
