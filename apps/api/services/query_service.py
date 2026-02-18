from __future__ import annotations

from azure.ai.inference.models import SystemMessage, UserMessage

from models.chat_models import ConversationMessage
from utils.azure_clients import get_rewrite_client

REWRITE_SYSTEM_PROMPT = """You are a query rewriting assistant. Your job is to rewrite a follow-up question into a standalone question that can be used for document retrieval.

Rules:
1. Resolve all pronouns and references using the conversation history
2. Expand abbreviations if context makes them clear
3. Keep the rewritten query concise and focused
4. If the query is already standalone, return it as-is
5. Output ONLY the rewritten query, nothing else"""


def rewrite_query(
    query: str,
    conversation_history: list[ConversationMessage],
) -> str:
    """Rewrite a follow-up query into a standalone query using GPT-5 Nano (low reasoning)."""
    if not conversation_history:
        return query

    client = get_rewrite_client()

    history_text = "\n".join(
        f"{msg.role}: {msg.content}" for msg in conversation_history
    )

    messages = [
        SystemMessage(content=REWRITE_SYSTEM_PROMPT),
        UserMessage(
            content=f"Conversation history:\n{history_text}\n\nFollow-up question: {query}\n\nRewritten standalone question:"
        ),
    ]

    response = client.complete(
        messages=messages,
        model_extras={"max_completion_tokens": 512, "reasoning_effort": "low"},
    )
    content = response.choices[0].message.content
    rewritten = content.strip() if content else ""
    return rewritten if rewritten else query
