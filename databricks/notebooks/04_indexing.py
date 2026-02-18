# Databricks notebook source

# COMMAND ----------
# MAGIC %md
# MAGIC # 04 - Indexing
# MAGIC
# MAGIC Reads chunks with embeddings from Delta table (filtered by chunk_ids from the previous task)
# MAGIC and uploads them to Azure AI Search in batches using upsert semantics.

# COMMAND ----------

dbutils.widgets.text("input_table", "rag_ingestion.chunks_with_embeddings", "Input Table")
dbutils.widgets.text("index_name", "rag-index", "Search Index Name")
dbutils.widgets.text("secrets_scope", "rag-ingestion", "Databricks Secrets Scope")
dbutils.widgets.text("upload_batch_size", "100", "Upload Batch Size")

# COMMAND ----------

import sys
import json
import time

import pyspark.sql.functions as F

sys.path.append("../")
from utils.azure_clients import get_search_client
from utils.quality_checks import validate_index_document

# COMMAND ----------

input_table = dbutils.widgets.get("input_table")
index_name = dbutils.widgets.get("index_name")
upload_batch_size = int(dbutils.widgets.get("upload_batch_size"))

# COMMAND ----------

# Get chunk_ids and org/folder context from the previous task (generate_embeddings)
chunk_ids_raw = dbutils.jobs.taskValues.get(taskKey="generate_embeddings", key="chunk_ids", default="")
organization_id = dbutils.jobs.taskValues.get(taskKey="generate_embeddings", key="organization_id", default="")
folder_id = dbutils.jobs.taskValues.get(taskKey="generate_embeddings", key="folder_id", default="")

if not chunk_ids_raw:
    print("No chunk IDs received from embedding task, nothing to index")
    dbutils.notebook.exit(json.dumps({"status": "SUCCESS", "success_count": 0, "error_count": 0}))

chunk_ids = [cid.strip() for cid in chunk_ids_raw.split(",") if cid.strip()]
print(f"Indexing {len(chunk_ids)} chunks")

# Get document IDs for status updates (extract from chunk IDs: "{doc_id}_chunk_{n}")
document_ids = list(set(cid.rsplit("_chunk_", 1)[0] for cid in chunk_ids))

from utils.db_status import update_document_status
db_url = dbutils.secrets.get(scope=dbutils.widgets.get("secrets_scope"), key="DATABASE_URL")

# COMMAND ----------

try:
    search_client = get_search_client(index_name)

    df = spark.table(input_table).filter(F.col("id").isin(chunk_ids))
    chunks = df.collect()
    print(f"Read {len(chunks)} chunks from {input_table}")

    documents = []
    validation_errors = []

    for row in chunks:
        r = row.asDict()
        doc = {
            "id": r["id"],
            "content": r["content"],
            "content_vector": list(r["content_vector"]),
            "document_id": r["document_id"],
            "document_name": r["document_name"],
            "document_url": r["document_url"],
            "page_number": r.get("page_number") or 0,
            "chunk_index": r["chunk_index"],
            "metadata": r.get("metadata", "{}"),
            "organization_id": r["organization_id"],
            "folder_id": r["folder_id"],
        }

        is_valid, errors = validate_index_document(doc)
        if not is_valid:
            validation_errors.extend(errors)

        documents.append(doc)

    if validation_errors:
        print(f"WARNING: {len(validation_errors)} validation issues found")
        for err in validation_errors[:10]:
            print(f"  - {err}")

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

    if error_count == 0:
        update_document_status(document_ids, "indexed", db_url)
    else:
        update_document_status(document_ids, "failed", db_url, error=f"{error_count} chunks failed to index")

except Exception as e:
    update_document_status(document_ids, "failed", db_url, error=f"Indexing failed: {e}")
    raise

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    "status": "SUCCESS" if error_count == 0 else "PARTIAL_SUCCESS",
    "success_count": success_count,
    "error_count": error_count,
}))
