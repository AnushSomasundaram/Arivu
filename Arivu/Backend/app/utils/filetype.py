"""File type detection from content-type header and filename extension."""

from __future__ import annotations

# Comprehensive list of supported file extensions
SUPPORTED_EXTENSIONS = {
    # Documents
    "pdf", "txt", "md", "rtf", "html", "htm", "xml", "epub",
    # Office
    "docx", "doc", "xlsx", "xls", "pptx", "ppt",
    # LibreOffice
    "odt", "ods", "odp",
    # Data
    "csv", "json", "jsonl", "yaml", "yml", "toml",
    # Code
    "py", "js", "ts", "jsx", "tsx", "java", "c", "cpp", "h", "hpp",
    "go", "rs", "sql", "sh", "bash", "ipynb",
    # Images (with OCR)
    "png", "jpg", "jpeg", "gif", "bmp", "tiff", "tif",
    # Email
    "eml", "msg",
}

MIME_TO_EXT: dict[str, str] = {
    # Documents
    "application/pdf": "pdf",
    "text/plain": "txt",
    "text/markdown": "md",
    "text/x-markdown": "md",
    "text/html": "html",
    "application/xhtml+xml": "html",
    "text/xml": "xml",
    "application/xml": "xml",
    "application/rtf": "rtf",
    "application/epub+zip": "epub",
    # Office - Word
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/msword": "doc",
    # Office - Excel
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.ms-excel": "xls",
    # Office - PowerPoint
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
    "application/vnd.ms-powerpoint": "ppt",
    # LibreOffice
    "application/vnd.oasis.opendocument.text": "odt",
    "application/vnd.oasis.opendocument.spreadsheet": "ods",
    "application/vnd.oasis.opendocument.presentation": "odp",
    # Data
    "text/csv": "csv",
    "application/json": "json",
    "application/x-yaml": "yaml",
    "text/yaml": "yaml",
    "application/toml": "toml",
    # Code
    "text/x-python": "py",
    "application/x-python-code": "py",
    "text/javascript": "js",
    "application/javascript": "js",
    "application/x-ipynb+json": "ipynb",
    # Images
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/bmp": "bmp",
    "image/tiff": "tiff",
    # Email
    "message/rfc822": "eml",
    "application/vnd.ms-outlook": "msg",
}


def detect_filetype(filename: str, content_type: str | None = None) -> str | None:
    """Return the canonical extension or None if unsupported."""
    # Try content-type first
    if content_type:
        ext = MIME_TO_EXT.get(content_type.split(";")[0].strip().lower())
        if ext:
            return ext

    # Fallback to filename extension
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix in SUPPORTED_EXTENSIONS:
        return suffix

    return None
