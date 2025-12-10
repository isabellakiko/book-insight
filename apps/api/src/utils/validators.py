"""Input validation utilities."""

import re
from fastapi import HTTPException


def validate_book_id(book_id: str) -> str:
    """Validate book ID format (12-char hex string).

    Args:
        book_id: The book ID to validate

    Returns:
        The validated book ID

    Raises:
        HTTPException: If the book ID format is invalid
    """
    if not book_id or not re.match(r"^[a-f0-9]{12}$", book_id):
        raise HTTPException(status_code=400, detail="Invalid book ID format")
    return book_id


def validate_character_name(name: str) -> str:
    """Validate character name for safety.

    Prevents path traversal and other injection attacks.

    Args:
        name: The character name to validate

    Returns:
        The validated and trimmed character name

    Raises:
        HTTPException: If the character name is invalid
    """
    if not name:
        raise HTTPException(status_code=400, detail="Character name is required")

    name = name.strip()

    if len(name) > 100:
        raise HTTPException(
            status_code=400, detail="Character name too long (max 100 chars)"
        )

    # Prevent path traversal and null byte injection
    dangerous_patterns = ["/", "\\", "..", "\x00"]
    if any(pattern in name for pattern in dangerous_patterns):
        raise HTTPException(
            status_code=400, detail="Invalid characters in character name"
        )

    return name


def validate_chapter_index(index: int, max_chapters: int) -> int:
    """Validate chapter index is within bounds.

    Args:
        index: The chapter index to validate
        max_chapters: The total number of chapters

    Returns:
        The validated chapter index

    Raises:
        HTTPException: If the index is out of bounds
    """
    if index < 0 or index >= max_chapters:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return index
