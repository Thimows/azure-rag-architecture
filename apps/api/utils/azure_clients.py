from functools import lru_cache

from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.storage.blob import BlobServiceClient

from config.settings import settings


@lru_cache
def get_openai_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version="2024-12-01-preview",
    )


@lru_cache
def get_search_client() -> SearchClient:
    return SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
    )


@lru_cache
def get_document_analysis_client() -> DocumentAnalysisClient:
    return DocumentAnalysisClient(
        endpoint=settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
        credential=AzureKeyCredential(settings.AZURE_DOCUMENT_INTELLIGENCE_KEY),
    )


@lru_cache
def get_blob_service_client() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(
        settings.AZURE_STORAGE_CONNECTION_STRING
    )
