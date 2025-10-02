from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from core.models.models import ChatRequest, ChatResponse
from core.services.chat_service import ChatService
from core.utils.database import AsyncDatabaseTool, chatbot_db_engine

chat_router = APIRouter(prefix="/api/chat", tags=["chat"])


@chat_router.post("")
async def chat(prompt: ChatRequest) -> ChatResponse:
    try:
        async with AsyncDatabaseTool(chatbot_db_engine).get_session() as session:
            chat_service = ChatService(session)
            return await chat_service.chat(prompt)
    except Exception as ex:
        raise HTTPException(
            status_code=500, detail=f"[chat][error] Internal Server Error: {ex}"
        )


@chat_router.post("/stream")
async def chat_stream(prompt: ChatRequest) -> StreamingResponse:
    try:
        async with AsyncDatabaseTool(chatbot_db_engine).get_session() as session:
            chat_service = ChatService(session)
            return await chat_service.chat_stream(prompt)
    except Exception as ex:
        raise HTTPException(
            status_code=500, detail=f"[chat_stream][error] Internal Server Error: {ex}"
        )
