import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
from docx import Document
import tempfile
import os


# Optional: Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from PDF files
    """
    pdf_reader = PdfReader(uploaded_file)

    text = ""

    for page in pdf_reader.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    return text


def extract_text_from_docx(uploaded_file):
    """
    Extract text from DOCX files
    """
    doc = Document(uploaded_file)

    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


def extract_text_from_image(uploaded_file):
    """
    Extract text from image using OCR
    """

    # Save temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    # Open image
    image = Image.open(temp_path)

    # OCR extraction
    text = pytesseract.image_to_string(image)

    # Delete temp file
    os.remove(temp_path)

    return text


def extract_text(uploaded_file):
    """
    Main extraction router
    """

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)

    elif file_name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)

    elif file_name.endswith((".png", ".jpg", ".jpeg")):
        return extract_text_from_image(uploaded_file)

    else:
        return "Unsupported file format"