from enum import Enum
from typing import Optional
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_mixin
from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, func, text
from database import Base
from sqlmodel import Field

class FeatureKey(str, Enum):
    ai_tim_kiem = "Hỏi Đáp"
    giai_bai_tap = "Giải Bài Tập"
    ai_viet_van = "AI Viết Văn"
    dich = "Dịch"
    tom_tat = "Tóm Tắt"
    mindmap = "Mindmap"


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"
    tool = "tool"


@declarative_mixin
class BaseModel():
    cre_dt = Column(DateTime(timezone=True), nullable=False, default=func.now())
    cre_usr_id = Column(String(20), nullable=False)
    upd_dt = Column(DateTime(timezone=True), nullable=False, default=func.now())
    upd_usr_id = Column(String(20), nullable=False)


class User(Base, BaseModel):
    __tablename__ = "users"
    usr_id = Column(String(20), primary_key=True, index=True)
    usr_nm = Column(String(50), nullable=False)
    usr_email = Column(String(100), unique=True, index=True)


class Conversation(Base, BaseModel):
    __tablename__ = "conversation"
    conversation_id: UUID = Column(UUID, primary_key=True, default=text("gen_random_uuid()"))
    title = Column(String)
    messages: Mapped[list["Messages"]] = relationship(
        "Messages",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )



class Messages(Base, BaseModel):
    __tablename__ = "messages"
    id: UUID = Column(UUID, primary_key=True, default=text("gen_random_uuid()"))
    conversation_id = Column(UUID, ForeignKey("conversation.conversation_id"), primary_key=True)
    role: Mapped[MessageRole] = mapped_column()   
    content: str = Column(String, nullable=True)
    metadata_: Optional[dict] = Column(JSONB, default=None),
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")