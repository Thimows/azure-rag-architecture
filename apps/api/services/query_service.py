from __future__ import annotations

from azure.ai.inference.models import SystemMessage, UserMessage

from models.chat_models import ConversationMessage
from utils.azure_clients import get_rewrite_client

REWRITE_SYSTEM_PROMPT = """Rewrite the user's latest message into a standalone search query for document retrieval, using conversation history to resolve references.

Rules:
1. If the message is conversational (greetings, thanks, acknowledgements, small talk) — return it EXACTLY as-is
2. Only rewrite when the message references earlier context (pronouns, "that", "it", etc.)
3. Keep rewrites concise — a short search query, not a full sentence
4. Output ONLY the rewritten query, nothing else"""


def rewrite_query(
    query: str,
    conversation_history: list[ConversationMessage],
) -> str:
    """Rewrite a follow-up query into a standalone query using GPT-5 Nano (low reasoning)."""
    if not conversation_history:
        return query

    client = get_rewrite_client()

    # Only include the last few turns for context
    recent = conversation_history[-6:]
    history_text = "\n".join(
        f"{msg.role}: {msg.content[:200]}" for msg in recent
    )

    messages = [
        SystemMessage(content=REWRITE_SYSTEM_PROMPT),
        UserMessage(
            content=f"History:\n{history_text}\n\nLatest message: {query}"
        ),
    ]

    response = client.complete(
        messages=messages,
        model_extras={"max_completion_tokens": 128, "reasoning_effort": "low"},
    )
    content = response.choices[0].message.content
    rewritten = content.strip().strip('"') if content else ""
    return rewritten if rewritten else query
