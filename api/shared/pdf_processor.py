"""
PDF processing utilities for extracting text from PDF files.
"""
import logging
import PyPDF2
from io import BytesIO

def extract_pdf_text(pdf_bytes: bytes, filename: str = "document.pdf") -> dict:
    """
    Extract text content from a PDF file.
    Returns dict with 'text' (extracted content), 'pages', and 'filename'.
    """
    logging.info(f'=== Starting PDF text extraction for: {filename} ===')
    
    try:
        pdf_file = BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        num_pages = len(pdf_reader.pages)
        logging.info(f"PDF has {num_pages} pages")
        
        if num_pages == 0:
            logging.error("PDF has no pages")
            return None
        
        # Extract text from all pages
        full_text = []
        for page_num in range(num_pages):
            try:
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    full_text.append(text)
            except Exception as e:
                logging.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
        
        combined_text = '\n\n'.join(full_text)
        
        if not combined_text or len(combined_text) < 50:
            logging.error(f"Extracted text too short: {len(combined_text)} characters")
            return None
        
        logging.info(f"Successfully extracted {len(combined_text)} characters from {num_pages} pages")
        return {
            'text': combined_text,
            'pages': num_pages,
            'filename': filename,
            'source': 'pdf'
        }
        
    except PyPDF2.errors.PdfReadError as e:
        logging.error(f"PDF read error: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error extracting PDF text: {str(e)}", exc_info=True)
        return None
