from typing import Optional, Any
from pydantic import BaseModel
from uuid import UUID


class RevelantDocChunk(BaseModel):
    chunk_id: str
    model: str
    vector: list[float]
    metadata: Any
    similarity_score: float


class ChatRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: UUID
    assistant_prompt: str
