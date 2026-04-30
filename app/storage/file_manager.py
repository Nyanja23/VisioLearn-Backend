"""
File Storage Manager for VisioLearn

Handles secure file storage, validation, and retrieval for lesson notes.
Supports PDF, DOCX, and TXT files for teacher lesson content uploads.
"""

import os
import uuid
import mimetypes
from pathlib import Path
from typing import Optional
from fastapi import HTTPException, UploadFile, status

# Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads/notes")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 25 * 1024 * 1024))  # 25 MB default

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".doc"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain"
}

# Magic bytes for file validation (first 4 bytes)
MAGIC_BYTES = {
    b"%PDF": ".pdf",
    b"PK\x03\x04": ".docx",  # ZIP-based format
    b"\xd0\xcf\x11\xe0": ".doc"  # OLE2 format
}


class FileStorageError(Exception):
    """Custom exception for file storage operations"""
    pass


class FileManager:
    """Manages file uploads, storage, and retrieval with validation"""

    @staticmethod
    def ensure_upload_dir() -> Path:
        """Create upload directory if it doesn't exist"""
        upload_path = Path(UPLOAD_DIR)
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path

    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """Validate file extension"""
        _, ext = os.path.splitext(filename)
        return ext.lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Validate file size doesn't exceed limit"""
        return file_size <= MAX_FILE_SIZE

    @staticmethod
    def validate_mime_type(content_type: Optional[str]) -> bool:
        """Validate MIME type"""
        if not content_type:
            return False
        # Handle charset suffix (e.g., "text/plain; charset=utf-8")
        base_type = content_type.split(";")[0].strip()
        return base_type in ALLOWED_MIME_TYPES

    @staticmethod
    def validate_magic_bytes(file_content: bytes) -> Optional[str]:
        """
        Validate file magic bytes to detect actual file type
        Returns expected extension if valid, None otherwise
        """
        for magic_bytes, ext in MAGIC_BYTES.items():
            if file_content.startswith(magic_bytes):
                return ext
        # TXT files don't have magic bytes, check if it's valid UTF-8
        try:
            file_content.decode("utf-8")
            return ".txt"
        except UnicodeDecodeError:
            pass
        return None

    @staticmethod
    async def save_upload_file(
        file: UploadFile,
        note_id: str
    ) -> str:
        """
        Save uploaded file to disk with validation

        Args:
            file: FastAPI UploadFile
            note_id: UUID of the LessonNote record

        Returns:
            Relative file path (e.g., "notes/{uuid}/filename.pdf")

        Raises:
            HTTPException: If file validation fails
        """
        FileManager.ensure_upload_dir()

        # Validate filename
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )

        if not FileManager.validate_file_extension(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Validate MIME type
        if not FileManager.validate_mime_type(file.content_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid MIME type: {file.content_type}"
            )

        # Read file content for validation
        content = await file.read()
        file_size = len(content)

        # Validate file size
        if not FileManager.validate_file_size(file_size):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed ({MAX_FILE_SIZE / 1024 / 1024:.0f} MB)"
            )

        # Validate magic bytes
        detected_ext = FileManager.validate_magic_bytes(content)
        if not detected_ext:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content doesn't match declared type"
            )

        # Extension mismatch warning (but allow it)
        _, claimed_ext = os.path.splitext(file.filename)
        if detected_ext != claimed_ext.lower():
            # Use detected extension for safety
            filename = f"{os.path.splitext(file.filename)[0]}{detected_ext}"
        else:
            filename = file.filename

        # Create directory structure: uploads/notes/{note_id}/
        note_dir = Path(UPLOAD_DIR) / str(note_id)
        note_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = note_dir / filename
        with open(file_path, "wb") as f:
            f.write(content)

        # Return relative path for database storage (relative to UPLOAD_DIR)
        # Since UPLOAD_DIR is ./uploads/notes, we only need the uuid/filename part
        relative_path = os.path.join(str(note_id), filename)
        return relative_path

    @staticmethod
    def get_file_full_path(relative_path: str) -> Path:
        """
        Get full file system path from relative path

        Args:
            relative_path: Relative path (e.g., "notes/{uuid}/filename.pdf")

        Returns:
            Full Path object
        """
        full_path = Path(UPLOAD_DIR) / relative_path
        return full_path

    @staticmethod
    def file_exists(relative_path: str) -> bool:
        """Check if file exists"""
        full_path = FileManager.get_file_full_path(relative_path)
        return full_path.exists() and full_path.is_file()

    @staticmethod
    def read_file(relative_path: str) -> bytes:
        """
        Read file content

        Args:
            relative_path: Relative path

        Returns:
            File content as bytes

        Raises:
            FileStorageError: If file not found
        """
        full_path = FileManager.get_file_full_path(relative_path)
        if not full_path.exists():
            raise FileStorageError(f"File not found: {relative_path}")
        return full_path.read_bytes()

    @staticmethod
    def delete_file(relative_path: str) -> bool:
        """
        Delete file from storage

        Args:
            relative_path: Relative path

        Returns:
            True if deleted, False if not found
        """
        full_path = FileManager.get_file_full_path(relative_path)
        if full_path.exists():
            full_path.unlink()
            # Try to remove empty directory
            try:
                full_path.parent.rmdir()
            except OSError:
                pass  # Directory not empty, ignore
            return True
        return False

    @staticmethod
    def get_file_info(relative_path: str) -> dict:
        """
        Get file information

        Args:
            relative_path: Relative path

        Returns:
            Dict with size, created_at, extension
        """
        full_path = FileManager.get_file_full_path(relative_path)
        if not full_path.exists():
            raise FileStorageError(f"File not found: {relative_path}")

        stat = full_path.stat()
        _, ext = os.path.splitext(full_path.name)

        return {
            "filename": full_path.name,
            "size_bytes": stat.st_size,
            "created_at": stat.st_ctime,
            "extension": ext
        }
