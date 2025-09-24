from fastapi import APIRouter, HTTPException
from services.chat import ChatService
from database import AsyncSessionLocal
from router.models.request import ConversationRequest, ConversationResponse
from repositories.models.models import Conversation
from uuid import UUID

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/saveConversation")
async def saveConversation(conversation: ConversationRequest) -> ConversationResponse:
    try:
        async with AsyncSessionLocal() as session:
            chat_service = ChatService(session)
            saved_conversation = await chat_service.conversation_repo.addConversation(Conversation(**conversation.model_dump()))
            return saved_conversation
    except Exception as ex:
        print(f"Something went wrong: {ex}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/getConversation")
async def getConversation(id: UUID) -> ConversationResponse:
    async with AsyncSessionLocal() as session:
        chat_service = ChatService(session)
        return await chat_service.conversation_repo.getConversation(id)
        