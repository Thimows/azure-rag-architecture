"""
Azure SDK client factories for Databricks notebooks.

All credentials are read from Databricks secrets scope "rag-ingestion".
Expected secrets:
  - azure-openai-endpoint
  - azure-openai-key
  - azure-openai-embedding-deployment
  - azure-search-endpoint
  - azure-search-key
  - azure-search-index-name
  - azure-storage-connection-string
  - document-intelligence-endpoint
  - document-intelligence-key
"""

from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.storage.blob import BlobServiceClient

SECRETS_SCOPE = "rag-ingestion"


def _get_dbutils():
    """Get dbutils from the Databricks runtime context."""
    from pyspark.dbutils import DBUtils
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    return DBUtils(spark)


def get_secret(key: str) -> str:
    """Read a secret from the Databricks secrets scope."""
    dbutils = _get_dbutils()
    return dbutils.secrets.get(scope=SECRETS_SCOPE, key=key)


def get_document_analysis_client() -> DocumentAnalysisClient:
    """Create DocumentAnalysisClient using Databricks secrets."""
    return DocumentAnalysisClient(
        endpoint=get_secret("document-intelligence-endpoint"),
        credential=AzureKeyCredential(get_secret("document-intelligence-key")),
    )


def get_openai_client() -> AzureOpenAI:
    """Create AzureOpenAI client using Databricks secrets."""
    return AzureOpenAI(
        azure_endpoint=get_secret("azure-openai-endpoint"),
        api_key=get_secret("azure-openai-key"),
        api_version="2024-12-01-preview",
    )


def get_search_client(index_name: str | None = None) -> SearchClient:
    """Create SearchClient using Databricks secrets."""
    return SearchClient(
        endpoint=get_secret("azure-search-endpoint"),
        index_name=index_name or get_secret("azure-search-index-name"),
        credential=AzureKeyCredential(get_secret("azure-search-key")),
    )


def get_search_index_client() -> SearchIndexClient:
    """Create SearchIndexClient for index management (create/update/delete)."""
    return SearchIndexClient(
        endpoint=get_secret("azure-search-endpoint"),
        credential=AzureKeyCredential(get_secret("azure-search-key")),
    )


def get_blob_service_client() -> BlobServiceClient:
    """Create BlobServiceClient using Databricks secrets."""
    return BlobServiceClient.from_connection_string(
        get_secret("azure-storage-connection-string")
    )
