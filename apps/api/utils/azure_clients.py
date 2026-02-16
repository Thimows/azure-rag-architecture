from functools import lru_cache

from azure.ai.inference import ChatCompletionsClient, EmbeddingsClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.storage.blob import BlobServiceClient

from config.settings import settings


@lru_cache
def get_chat_client() -> ChatCompletionsClient:
    return ChatCompletionsClient(
        endpoint=f"https://{settings.AZURE_AI_RESOURCE_NAME}.services.ai.azure.com/models",
        credential=AzureKeyCredential(settings.AZURE_AI_KEY),
        model=settings.AZURE_AI_CHAT_DEPLOYMENT,
    )


@lru_cache
def get_embeddings_client() -> EmbeddingsClient:
    return EmbeddingsClient(
        endpoint=f"https://{settings.AZURE_AI_RESOURCE_NAME}.services.ai.azure.com/models",
        credential=AzureKeyCredential(settings.AZURE_AI_KEY),
        model=settings.AZURE_AI_EMBEDDING_DEPLOYMENT,
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
