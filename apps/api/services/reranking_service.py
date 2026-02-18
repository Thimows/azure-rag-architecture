from __future__ import annotations

import json
import logging

from azure.ai.inference.models import SystemMessage, UserMessage

from config.settings import settings
from models.chat_models import SearchChunk
from utils.azure_clients import get_rewrite_client

logger = logging.getLogger(__name__)

RERANK_SYSTEM_PROMPT = """You are a relevance ranker. Given a query and numbered document chunks, return ONLY a JSON array of chunk numbers ordered by relevance to the query (most relevant first). Return at most {top_k} numbers.

Rules:
1. Only return chunk numbers that are actually relevant to the query
2. Output ONLY a valid JSON array of integers, nothing else
3. Example: [3, 1, 7, 2]"""

MAX_CHUNK_CHARS = 300


def rerank_chunks(
    query: str,
    chunks: list[SearchChunk],
    top_k: int | None = None,
) -> list[SearchChunk]:
    """Rerank chunks using GPT-5 Nano.

    Sends all chunks in a single prompt and asks the model to return
    ranked indices as a JSON array. Minimal output tokens for speed.
    """
    if top_k is None:
        top_k = settings.CONTEXT_TOP_K

    if not chunks:
        return []

    client = get_rewrite_client()

    # Build numbered chunk list, truncated for token efficiency
    chunk_lines = []
    for i, chunk in enumerate(chunks):
        text = chunk.content[:MAX_CHUNK_CHARS]
        if len(chunk.content) > MAX_CHUNK_CHARS:
            text += "..."
        chunk_lines.append(f"[{i}] {text}")

    chunks_text = "\n\n".join(chunk_lines)

    messages = [
        SystemMessage(content=RERANK_SYSTEM_PROMPT.format(top_k=top_k)),
        UserMessage(content=f"Query: {query}\n\nChunks:\n{chunks_text}"),
    ]

    response = client.complete(
        messages=messages,
        model_extras={"max_completion_tokens": 256, "reasoning_effort": "low"},
    )

    content = response.choices[0].message.content or ""

    try:
        ranked_indices = json.loads(content.strip())
        if not isinstance(ranked_indices, list):
            raise ValueError("Expected a JSON array")
    except (json.JSONDecodeError, ValueError):
        logger.warning("Rerank JSON parse failed, falling back to search order: %s", content)
        return chunks[:top_k]

    # Map indices back to chunks, skipping any out-of-range values
    reranked = []
    seen = set()
    for idx in ranked_indices:
        if isinstance(idx, int) and 0 <= idx < len(chunks) and idx not in seen:
            reranked.append(chunks[idx])
            seen.add(idx)
        if len(reranked) >= top_k:
            break

    return reranked
