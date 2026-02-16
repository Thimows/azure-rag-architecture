from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream():
    return {"message": "not implemented"}


@router.post("/query")
async def chat_query():
    return {"message": "not implemented"}
