"""Utility for updating document status in PostgreSQL from Databricks notebooks."""

import psycopg2


def update_document_status(
    document_ids: list[str],
    status: str,
    db_url: str,
    error: str | None = None,
) -> None:
    """Update document status in PostgreSQL.

    Args:
        document_ids: List of document UUIDs to update.
        status: New status value (e.g. "processing", "indexed", "failed").
        db_url: PostgreSQL connection string.
        error: Optional error message (set when status is "failed").
    """
    if not document_ids or not db_url:
        print(f"Skipping DB status update (no doc IDs or no DB URL)")
        return

    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE document SET status = %s, error = %s, updated_at = NOW() WHERE id = ANY(%s)",
                (status, error, document_ids),
            )
        conn.commit()
        print(f"Updated {len(document_ids)} documents to status '{status}'")
    finally:
        conn.close()
