"""
Quality checks for the ingestion pipeline.

Validates chunk quality, embedding integrity, and metadata completeness
at each pipeline stage.
"""

import math

import tiktoken

ENCODING = tiktoken.get_encoding("cl100k_base")


def validate_parsed_document(doc: dict) -> tuple[bool, list[str]]:
    """Validate a parsed document result."""
    errors = []

    if not doc.get("content"):
        errors.append("content is empty")
    if not doc.get("document_id"):
        errors.append("document_id is missing")
    if not doc.get("document_name"):
        errors.append("document_name is missing")
    if doc.get("page_count", 0) <= 0:
        errors.append("page_count must be > 0")

    return (len(errors) == 0, errors)


def validate_chunks(
    chunks: list[dict],
    min_tokens: int = 10,
    max_tokens: int = 600,
) -> tuple[bool, list[str]]:
    """Validate chunk quality."""
    errors = []

    for i, chunk in enumerate(chunks):
        content = chunk.get("content", "")
        if not content:
            errors.append(f"chunk {i}: content is empty")
            continue

        token_count = len(ENCODING.encode(content))
        if token_count < min_tokens:
            errors.append(f"chunk {i}: only {token_count} tokens (min {min_tokens})")
        if token_count > max_tokens:
            errors.append(f"chunk {i}: {token_count} tokens exceeds max {max_tokens}")

        if chunk.get("metadata") is None:
            errors.append(f"chunk {i}: metadata is missing")

    return (len(errors) == 0, errors)


def validate_embeddings(
    embeddings: list[list[float]],
    expected_dim: int = 3072,
) -> tuple[bool, list[str]]:
    """Validate embedding vectors."""
    errors = []

    for i, emb in enumerate(embeddings):
        if len(emb) != expected_dim:
            errors.append(f"embedding {i}: got {len(emb)} dims, expected {expected_dim}")
        if all(v == 0.0 for v in emb):
            errors.append(f"embedding {i}: all zeros (failed generation)")
        if any(math.isnan(v) or math.isinf(v) for v in emb):
            errors.append(f"embedding {i}: contains NaN or Inf")

    return (len(errors) == 0, errors)


def validate_index_document(doc: dict) -> tuple[bool, list[str]]:
    """Validate a document ready for Search indexing."""
    errors = []

    for field in ("id", "content", "content_vector", "document_id", "document_name"):
        if not doc.get(field):
            errors.append(f"'{field}' is missing or empty")

    vector = doc.get("content_vector", [])
    if vector and len(vector) != 3072:
        errors.append(f"content_vector has {len(vector)} dims, expected 3072")

    if not isinstance(doc.get("page_number", 0), int):
        errors.append("page_number must be an integer")
    if not isinstance(doc.get("chunk_index", 0), int):
        errors.append("chunk_index must be an integer")

    return (len(errors) == 0, errors)
