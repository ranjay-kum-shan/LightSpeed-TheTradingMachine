"""Atomic local-file replacement primitives."""

import os
from pathlib import Path
from uuid import uuid4

from trading_bot.storage.errors import AtomicWriteError


def atomic_write_bytes(path: Path, content: bytes) -> None:
    """Flush bytes to a same-directory temporary file before replacement."""

    temporary_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("xb") as output:
            bytes_written = output.write(content)
            if bytes_written != len(content):
                raise OSError("atomic file write was incomplete")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_path, path)
    except BaseException as error:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError as cleanup_error:
            raise AtomicWriteError("atomic file replacement cleanup failed") from cleanup_error
        if isinstance(error, OSError):
            raise AtomicWriteError("atomic file replacement failed") from error
        raise


def atomic_write_text(path: Path, content: str) -> None:
    """Encode text as UTF-8 and replace the target atomically."""

    try:
        encoded = content.encode("utf-8")
    except UnicodeError as error:
        raise AtomicWriteError("atomic text encoding failed") from error
    atomic_write_bytes(path, encoded)