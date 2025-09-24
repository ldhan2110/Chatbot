from pydantic import BaseModel
from uuid import UUID

class ConversationRequest(BaseModel):
    title: str
    cre_usr_id: str
    upd_usr_id: str

class ConversationResponse(BaseModel):
    conversation_id: UUID
    title: str
    cre_usr_id: str
    upd_usr_id: str

    class Config:
        orm_mode = True