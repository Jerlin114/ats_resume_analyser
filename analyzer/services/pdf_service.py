"""
PDF Extraction Service for ResumeIQ.

Extracts text from uploaded PDF resumes in-memory using PyMuPDF (fitz).
Strictly adheres to privacy requirements:
- Resumes are NEVER persisted to disk or permanent storage.
- Resume contents are NEVER logged or retained in application logs.
- Memory is released immediately after extraction.
"""

from typing import Tuple


class PDFExtractionError(Exception):
    """Custom exception raised when PDF validation or extraction fails."""
    pass


def extract_text_from_pdf(file_obj, max_size_mb: int = 5) -> str:
    """
    Extract text content from an in-memory PDF file object.

    Args:
        file_obj: UploadedFile or file-like object containing PDF bytes.
        max_size_mb: Maximum allowed file size in Megabytes (default: 5MB).

    Returns:
        str: Extracted clean text from the PDF.

    Raises:
        PDFExtractionError: If validation fails or PDF cannot be parsed.
    """
    # 1. Validate file object presence
    if not file_obj:
        raise PDFExtractionError("No resume file was uploaded.")

    # 2. Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    size = getattr(file_obj, 'size', None)
    if size is not None and size > max_size_bytes:
        raise PDFExtractionError(
            f"File size exceeds the limit of {max_size_mb} MB (uploaded size: {size / (1024 * 1024):.2f} MB)."
        )

    # 3. Read file content in-memory
    try:
        # If file_obj was previously read, reset cursor
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        file_bytes = file_obj.read()
    except Exception as exc:
        raise PDFExtractionError(f"Unable to read uploaded file: {str(exc)}") from exc

    # Secondary size check on actual byte length
    if len(file_bytes) > max_size_bytes:
        raise PDFExtractionError(
            f"File size exceeds the limit of {max_size_mb} MB."
        )

    if len(file_bytes) == 0:
        raise PDFExtractionError("The uploaded file is empty (0 bytes).")

    # 4. Validate PDF magic signature (%PDF-)
    if not file_bytes.startswith(b"%PDF-"):
        raise PDFExtractionError("Invalid file type: File is not a valid PDF document.")

    # 5. Extract text using PyMuPDF
    try:
        try:
            import pymupdf as fitz  # PyMuPDF 2.x+
        except ImportError:
            import fitz  # PyMuPDF 1.x
    except ImportError as err:
        raise PDFExtractionError(
            "PyMuPDF is not installed in the environment. Please run: pip install pymupdf"
        ) from err

    extracted_pages = []
    doc = None
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        if doc.is_encrypted:
            raise PDFExtractionError(
                "The PDF is password protected. Please upload an unlocked PDF resume."
            )

        if doc.page_count == 0:
            raise PDFExtractionError("The uploaded PDF contains no pages.")

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            if page_text:
                extracted_pages.append(page_text.strip())

    except PDFExtractionError:
        raise
    except Exception as exc:
        raise PDFExtractionError(f"Error extracting text from PDF: {str(exc)}") from exc
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass
        # Clean up local reference to raw bytes to free memory
        del file_bytes

    combined_text = "\n\n".join(extracted_pages).strip()

    if not combined_text:
        raise PDFExtractionError(
            "No readable text found in the PDF. Scanned image-only PDFs or encrypted documents without text layers are not supported. Please upload a text-based PDF."
        )

    return combined_text
