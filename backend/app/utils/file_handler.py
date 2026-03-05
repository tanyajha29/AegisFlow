import os
import shutil
import uuid
from pathlib import Path
from typing import Tuple

from fastapi import HTTPException, UploadFile, status

from ..config import get_settings


settings = get_settings()
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _validate_extension(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in settings.allowed_file_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type {ext}. Allowed: {', '.join(sorted(settings.allowed_file_types))}",
        )


def _validate_size(content: bytes) -> None:
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.max_upload_size_mb} MB limit",
        )


def save_upload_file(upload_file: UploadFile) -> Tuple[Path, bytes]:
    _validate_extension(upload_file.filename or "")
    content = upload_file.file.read()
    _validate_size(content)

    safe_name = f"{uuid.uuid4().hex}_{Path(upload_file.filename).name}"
    file_path = UPLOAD_DIR / safe_name
    with open(file_path, "wb") as f:
        f.write(content)

    return file_path, content


def save_code_as_file(code: str, file_name: str = "pasted_code.py") -> Path:
    _validate_extension(file_name)
    content = code.encode("utf-8")
    _validate_size(content)

    safe_name = f"{uuid.uuid4().hex}_{file_name}"
    file_path = UPLOAD_DIR / safe_name
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


def cleanup_file(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        # Best-effort cleanup
        pass


def cleanup_all_uploads() -> None:
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

