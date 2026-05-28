from pathlib import Path


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024


def extract_text_from_file(path: Path) -> str:
    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported file type '{extension}'. Use one of: {allowed}.")

    if extension == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")

    if extension == ".pdf":
        return _extract_pdf_text(path)

    return _extract_docx_text(path)


def _extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Install pypdf to parse PDF resumes.") from exc

    try:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise ValueError("Could not read PDF text. Try uploading a text-based PDF.") from exc

    return "\n".join(pages)


def _extract_docx_text(path: Path) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError("Install python-docx to parse DOCX resumes.") from exc

    try:
        document = Document(str(path))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
    except Exception as exc:
        raise ValueError("Could not read DOCX text. Check that the file is a valid .docx document.") from exc

    return "\n".join(paragraphs)
