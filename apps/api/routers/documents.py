import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from config.settings import settings
from models.document_models import (
    DocumentListItem,
    DocumentListResponse,
    DocumentUploadResponse,
    generate_document_id,
)
from utils.azure_clients import get_blob_service_client

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile):
    """Upload a document to Azure Blob Storage for ingestion."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )

    blob_service = get_blob_service_client()
    container_client = blob_service.get_container_client(settings.AZURE_STORAGE_CONTAINER_NAME)

    blob_client = container_client.get_blob_client(file.filename)
    blob_client.upload_blob(contents, overwrite=True)

    document_id = generate_document_id(file.filename)

    return DocumentUploadResponse(
        document_id=document_id,
        document_name=file.filename,
        status="uploaded",
        message="Document uploaded successfully. Run the ingestion pipeline to process it.",
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    """List all documents in the storage container."""
    blob_service = get_blob_service_client()
    container_client = blob_service.get_container_client(settings.AZURE_STORAGE_CONTAINER_NAME)

    documents = []
    for blob in container_client.list_blobs():
        ext = "." + blob.name.rsplit(".", 1)[-1].lower() if "." in blob.name else ""
        if ext not in ALLOWED_EXTENSIONS:
            continue

        documents.append(
            DocumentListItem(
                document_id=generate_document_id(blob.name),
                document_name=blob.name,
                size_bytes=blob.size,
                uploaded_at=blob.last_modified.isoformat() if blob.last_modified else "",
            )
        )

    return DocumentListResponse(documents=documents)
