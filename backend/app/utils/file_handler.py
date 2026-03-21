import os
import re
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


def strip_generated_prefix(filename: str) -> str:
    """
    Remove the leading UUID/hex prefix we add for safe storage so we can show the
    original file name back to the user. If the prefix is not a 32‑char hex block,
    the name is returned unchanged.
    """
    name = Path(filename).name
    if "_" not in name:
        return name
    prefix, rest = name.split("_", 1)
    if len(prefix) == 32 and re.fullmatch(r"[0-9a-fA-F]{32}", prefix):
        return rest
    return name


def save_upload_file(upload_file: UploadFile) -> Tuple[Path, bytes, str]:
    _validate_extension(upload_file.filename or "")
    content = upload_file.file.read()
    _validate_size(content)

    original_name = Path(upload_file.filename or "upload.bin").name
    safe_name = f"{uuid.uuid4().hex}_{original_name}"
    file_path = UPLOAD_DIR / safe_name
    with open(file_path, "wb") as f:
        f.write(content)

    return file_path, content, original_name


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
