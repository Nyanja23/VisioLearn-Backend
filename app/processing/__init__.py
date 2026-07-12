"""VisioLearn content processing module.

Only text extraction lives on the server. Question generation, summarising,
and lesson segmentation all run ON THE STUDENT'S DEVICE — that is what makes
the app offline-first and keeps this service small enough for a free tier.
The old Celery/spaCy pipeline was removed once the on-device engine became
the source of truth.
"""

from .text_extractor import extract_from_file, sanitize_text, TextExtractionError

__all__ = [
    "extract_from_file",
    "sanitize_text",
    "TextExtractionError",
]
