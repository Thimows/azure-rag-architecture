# Databricks notebook source

# COMMAND ----------
# MAGIC %md
# MAGIC # 01 — Document Parsing
# MAGIC
# MAGIC Reads documents from Azure Blob Storage, parses them via Azure Document Intelligence,
# MAGIC and writes parsed results to a Delta table for downstream processing.

# COMMAND ----------

dbutils.widgets.text("storage_container", "documents", "Storage Container Name")
dbutils.widgets.text("secrets_scope", "rag-ingestion", "Databricks Secrets Scope")
dbutils.widgets.text("output_table", "rag_ingestion.parsed_documents", "Output Delta Table")
dbutils.widgets.text("document_prefix", "", "Blob prefix filter (optional)")

# COMMAND ----------

import sys
import json
import uuid
from datetime import datetime

sys.path.append("../")
from utils.azure_clients import get_document_analysis_client, get_blob_service_client
from utils.quality_checks import validate_parsed_document

# COMMAND ----------

container_name = dbutils.widgets.get("storage_container")
output_table = dbutils.widgets.get("output_table")
document_prefix = dbutils.widgets.get("document_prefix")

blob_client = get_blob_service_client()
doc_intel_client = get_document_analysis_client()
container_client = blob_client.get_container_client(container_name)

# COMMAND ----------

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
blobs = []
for blob in container_client.list_blobs(name_starts_with=document_prefix or None):
    ext = "." + blob.name.rsplit(".", 1)[-1].lower() if "." in blob.name else ""
    if ext in SUPPORTED_EXTENSIONS:
        blobs.append(blob)

print(f"Found {len(blobs)} documents to process")

# COMMAND ----------

parsed_documents = []

for blob in blobs:
    document_id = str(uuid.uuid5(uuid.NAMESPACE_URL, blob.name))
    print(f"Processing: {blob.name} (id: {document_id})")

    blob_data = container_client.download_blob(blob.name).readall()
    ext = blob.name.rsplit(".", 1)[-1].lower()

    if ext == "txt":
        content = blob_data.decode("utf-8")
        parsed_doc = {
            "document_id": document_id,
            "document_name": blob.name,
            "document_url": f"https://{blob_client.account_name}.blob.core.windows.net/{container_name}/{blob.name}",
            "content": content,
            "pages": [{"page_number": 1, "content": content, "layout": []}],
            "page_count": 1,
            "parsed_at": datetime.utcnow().isoformat(),
        }
    else:
        content_type = (
            "application/pdf" if ext == "pdf"
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        poller = doc_intel_client.begin_analyze_document(
            "prebuilt-layout",
            document=blob_data,
            content_type=content_type,
        )
        result = poller.result()

        pages_data = []
        for page in result.pages:
            page_content = ""
            page_layout = []
            for paragraph in result.paragraphs:
                if any(br.page_number == page.page_number for br in paragraph.bounding_regions):
                    page_content += paragraph.content + "\n"
                    page_layout.append({
                        "content": paragraph.content,
                        "role": getattr(paragraph, "role", None),
                        "bounding_regions": [
                            {"page_number": br.page_number}
                            for br in paragraph.bounding_regions
                        ],
                    })
            pages_data.append({
                "page_number": page.page_number,
                "content": page_content.strip(),
                "layout": page_layout,
            })

        full_content = "\n\n".join(p["content"] for p in pages_data if p["content"])

        parsed_doc = {
            "document_id": document_id,
            "document_name": blob.name,
            "document_url": f"https://{blob_client.account_name}.blob.core.windows.net/{container_name}/{blob.name}",
            "content": full_content,
            "pages": pages_data,
            "page_count": len(pages_data),
            "parsed_at": datetime.utcnow().isoformat(),
        }

    is_valid, errors = validate_parsed_document(parsed_doc)
    if not is_valid:
        print(f"  WARNING: Validation issues for {blob.name}: {errors}")

    parsed_documents.append(parsed_doc)

print(f"Parsed {len(parsed_documents)} documents successfully")

# COMMAND ----------

for doc in parsed_documents:
    doc["pages_json"] = json.dumps(doc["pages"])
    del doc["pages"]

df = spark.createDataFrame(parsed_documents)
df.write.mode("overwrite").saveAsTable(output_table)

print(f"Wrote {df.count()} parsed documents to {output_table}")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({"status": "SUCCESS", "document_count": len(parsed_documents)}))
