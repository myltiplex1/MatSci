from pypdf import PdfReader
import logging
from logger import setup_logger

logger = setup_logger('pdf_utils')

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if not text.strip():
            logger.warning(f"No text extracted from {pdf_path}")
        else:
            logger.info(f"Successfully extracted text from {pdf_path}")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
        raise