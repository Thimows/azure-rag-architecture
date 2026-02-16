# Databricks notebook source

# COMMAND ----------
# MAGIC %md
# MAGIC # 00 — Create/Update Azure AI Search Index
# MAGIC
# MAGIC Creates the search index with vector, keyword, and semantic search configuration.
# MAGIC This is an idempotent operation — safe to re-run.

# COMMAND ----------

dbutils.widgets.text("index_name", "rag-index", "Search Index Name")
dbutils.widgets.text("secrets_scope", "rag-ingestion", "Databricks Secrets Scope")

# COMMAND ----------

import sys
sys.path.append("../")

from utils.azure_clients import get_search_index_client

# COMMAND ----------

from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticSearch,
    SemanticPrioritizedFields,
    SemanticField,
)

# COMMAND ----------

index_name = dbutils.widgets.get("index_name")

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
    SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=3072,
        vector_search_profile_name="vector-profile",
    ),
    SimpleField(name="document_id", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="document_name", type=SearchFieldDataType.String, filterable=True, facetable=True),
    SimpleField(name="document_url", type=SearchFieldDataType.String, filterable=False),
    SimpleField(name="page_number", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
    SimpleField(name="chunk_index", type=SearchFieldDataType.Int32, filterable=True),
    SimpleField(name="metadata", type=SearchFieldDataType.String, searchable=False),
]

vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="hnsw-config",
            parameters={"m": 4, "ef_construction": 400, "ef_search": 500, "metric": "cosine"},
        ),
    ],
    profiles=[
        VectorSearchProfile(name="vector-profile", algorithm_configuration_name="hnsw-config"),
    ],
)

semantic_config = SemanticConfiguration(
    name="semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        content_fields=[SemanticField(field_name="content")],
        title_field=SemanticField(field_name="document_name"),
    ),
)

semantic_search = SemanticSearch(configurations=[semantic_config])

index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search,
    semantic_search=semantic_search,
)

# COMMAND ----------

client = get_search_index_client()
result = client.create_or_update_index(index)
print(f"Index '{result.name}' created/updated successfully.")
print(f"Fields: {[f.name for f in result.fields]}")

# COMMAND ----------

dbutils.notebook.exit("SUCCESS")
