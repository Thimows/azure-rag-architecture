# Databricks notebook source

# COMMAND ----------
# MAGIC %md
# MAGIC # 04 — Indexing
# MAGIC
# MAGIC Reads chunks with embeddings from Delta table and uploads them to Azure AI Search
# MAGIC in batches using upsert semantics.

# COMMAND ----------

dbutils.widgets.text("input_table", "rag_ingestion.chunks_with_embeddings", "Input Table")
dbutils.widgets.text("index_name", "rag-index", "Search Index Name")
dbutils.widgets.text("secrets_scope", "rag-ingestion", "Databricks Secrets Scope")
dbutils.widgets.text("upload_batch_size", "100", "Upload Batch Size")

# COMMAND ----------

import sys
import json
import time

sys.path.append("../")
from utils.azure_clients import get_search_client
from utils.quality_checks import validate_index_document

# COMMAND ----------

input_table = dbutils.widgets.get("input_table")
index_name = dbutils.widgets.get("index_name")
upload_batch_size = int(dbutils.widgets.get("upload_batch_size"))

# COMMAND ----------

search_client = get_search_client(index_name)

# COMMAND ----------

df = spark.table(input_table)
chunks = df.collect()
print(f"Uploading {len(chunks)} chunks to index '{index_name}'")

# COMMAND ----------

documents = []
validation_errors = []

for row in chunks:
    doc = {
        "id": row["id"],
        "content": row["content"],
        "content_vector": list(row["content_vector"]),
        "document_id": row["document_id"],
        "document_name": row["document_name"],
        "document_url": row["document_url"],
        "page_number": row.get("page_number") or 0,
        "chunk_index": row["chunk_index"],
        "metadata": row.get("metadata", "{}"),
    }

    is_valid, errors = validate_index_document(doc)
    if not is_valid:
        validation_errors.extend(errors)

    documents.append(doc)

if validation_errors:
    print(f"WARNING: {len(validation_errors)} validation issues found")
    for err in validation_errors[:10]:
        print(f"  - {err}")

# COMMAND ----------

total_batches = (len(documents) + upload_batch_size - 1) // upload_batch_size
success_count = 0
error_count = 0

for batch_idx in range(total_batches):
    start = batch_idx * upload_batch_size
    end = min(start + upload_batch_size, len(documents))
    batch = documents[start:end]

    try:
        result = search_client.merge_or_upload_documents(batch)
        succeeded = sum(1 for r in result if r.succeeded)
        failed = sum(1 for r in result if not r.succeeded)
        success_count += succeeded
        error_count += failed

        if failed > 0:
            for r in result:
                if not r.succeeded:
                    print(f"  Failed: {r.key} - {r.error_message}")

        print(f"  Batch {batch_idx + 1}/{total_batches}: {succeeded} succeeded, {failed} failed")
    except Exception as e:
        print(f"  Batch {batch_idx + 1}/{total_batches} FAILED: {e}")
        error_count += len(batch)

    if batch_idx < total_batches - 1:
        time.sleep(0.5)

print(f"\nIndexing complete: {success_count} succeeded, {error_count} failed")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    "status": "SUCCESS" if error_count == 0 else "PARTIAL_SUCCESS",
    "success_count": success_count,
    "error_count": error_count,
}))
