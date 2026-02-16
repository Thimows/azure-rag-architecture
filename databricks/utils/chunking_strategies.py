"""
Chunking strategies for document text.

Three strategies:
1. Semantic chunking — preserves sentence boundaries
2. Structure-aware chunking — respects document hierarchy (headers, sections)
3. Sliding window chunking — fixed-size windows with overlap

All strategies produce chunks as list[dict] with keys:
  - content: str
  - chunk_index: int
  - metadata: dict
"""

import re

import tiktoken

ENCODING = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Count tokens using the cl100k_base tokenizer."""
    return len(ENCODING.encode(text))


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using regex boundary detection."""
    pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    parts = re.split(pattern, text)
    return [s.strip() for s in parts if s.strip()]


def semantic_chunker(
    text: str,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
    page_number: int | None = None,
) -> list[dict]:
    """
    Chunk text by preserving sentence boundaries.

    Accumulates sentences until max_tokens is reached, then starts a new chunk
    with overlap from the end of the previous chunk.
    """
    if not text.strip():
        return []

    sentences = _split_into_sentences(text)
    chunks = []
    current_sentences: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

        if current_tokens + sentence_tokens > max_tokens and current_sentences:
            chunk_text = " ".join(current_sentences)
            chunks.append({
                "content": chunk_text,
                "chunk_index": len(chunks),
                "page_number": page_number,
                "metadata": {"strategy": "semantic", "token_count": current_tokens},
            })

            # Build overlap from trailing sentences
            overlap_sentences: list[str] = []
            overlap_count = 0
            for s in reversed(current_sentences):
                s_tokens = count_tokens(s)
                if overlap_count + s_tokens > overlap_tokens:
                    break
                overlap_sentences.insert(0, s)
                overlap_count += s_tokens

            current_sentences = overlap_sentences
            current_tokens = overlap_count

        current_sentences.append(sentence)
        current_tokens += sentence_tokens

    # Final chunk
    if current_sentences:
        chunk_text = " ".join(current_sentences)
        chunks.append({
            "content": chunk_text,
            "chunk_index": len(chunks),
            "page_number": page_number,
            "metadata": {"strategy": "semantic", "token_count": count_tokens(chunk_text)},
        })

    return chunks


def structure_aware_chunker(
    text: str,
    layout_data: list[dict],
    max_tokens: int = 512,
) -> list[dict]:
    """
    Chunk text respecting document structure from Document Intelligence layout.

    Groups paragraphs by section headings. If a section exceeds max_tokens,
    falls back to semantic_chunker within that section.
    """
    if not layout_data:
        return semantic_chunker(text, max_tokens=max_tokens)

    # Group paragraphs by section
    sections: list[dict] = []
    current_section = {"title": None, "paragraphs": []}

    for para in layout_data:
        role = para.get("role")
        content = para.get("content", "")
        if not content.strip():
            continue

        if role == "sectionHeading":
            if current_section["paragraphs"]:
                sections.append(current_section)
            current_section = {"title": content, "paragraphs": []}
        else:
            current_section["paragraphs"].append(content)

    if current_section["paragraphs"]:
        sections.append(current_section)

    # Convert sections to chunks
    chunks = []
    for section in sections:
        section_text = "\n".join(section["paragraphs"])
        section_tokens = count_tokens(section_text)

        if section_tokens <= max_tokens:
            chunks.append({
                "content": section_text,
                "chunk_index": len(chunks),
                "page_number": None,
                "metadata": {
                    "strategy": "structure_aware",
                    "section_title": section["title"],
                    "token_count": section_tokens,
                },
            })
        else:
            # Section too large — fall back to semantic chunking within it
            sub_chunks = semantic_chunker(section_text, max_tokens=max_tokens)
            for sub in sub_chunks:
                sub["chunk_index"] = len(chunks)
                sub["metadata"]["section_title"] = section["title"]
                sub["metadata"]["strategy"] = "structure_aware"
                chunks.append(sub)

    return chunks


def sliding_window_chunker(
    text: str,
    window_size: int = 512,
    overlap: int = 50,
    page_number: int | None = None,
) -> list[dict]:
    """
    Fixed-size sliding window chunking by token count.

    Tokenizes text, slides a window with stride = window_size - overlap,
    and decodes each window back to text.
    """
    if not text.strip():
        return []

    tokens = ENCODING.encode(text)
    stride = max(window_size - overlap, 1)
    chunks = []

    for start in range(0, len(tokens), stride):
        end = min(start + window_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = ENCODING.decode(chunk_tokens)

        chunks.append({
            "content": chunk_text,
            "chunk_index": len(chunks),
            "page_number": page_number,
            "metadata": {
                "strategy": "sliding_window",
                "token_count": len(chunk_tokens),
            },
        })

        if end >= len(tokens):
            break

    return chunks
