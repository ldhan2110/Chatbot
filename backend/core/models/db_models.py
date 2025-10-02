from enum import Enum
from sqlalchemy import (
    UUID,
    Column,
    BigInteger,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    String,
    text,
    func,
)
from sqlalchemy.sql import expression
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, relationship, declarative_mixin
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()


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
    cre_dt = Column(DateTime(timezone=True),
                    nullable=False, default=func.now())
    cre_usr_id = Column(String(20), nullable=False)
    upd_dt = Column(DateTime(timezone=True),
                    nullable=False, default=func.now())
    upd_usr_id = Column(String(20), nullable=False)


class User(Base, BaseModel):
    __tablename__ = "users"

    usr_id = Column(String(20), primary_key=True, index=True)
    usr_nm = Column(String(50), nullable=False)
    usr_email = Column(String(100), unique=True, index=True)


class Conversation(Base, BaseModel):
    __tablename__ = "conversation"

    conversation_id: Mapped["UUID"] = Column(
        UUID, primary_key=True, default=text("gen_random_uuid()"))
    title = Column(String)
    message_runs: Mapped[list["ConversationMessageRun"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan")


class ConversationMessageRun(Base, BaseModel):
    __tablename__ = "conversation_message_run"

    id: Mapped["UUID"] = Column(
        UUID, primary_key=True, default=text("gen_random_uuid()"))
    conversation_id: UUID = Column(UUID, ForeignKey(
        "conversation.conversation_id"), nullable=False, index=True)
    messages: dict | list = Column(
        "messages", JSONB, nullable=False, default=list)
    conversation: Mapped["Conversation"] = relationship(
        back_populates="message_runs")


class DocChunk(Base):
    __tablename__ = "doc_chunks"

    chunk_id = Column(BigInteger, primary_key=True, autoincrement=True)
    text = Column("text", Text, nullable=False)
    token_count = Column(Integer, nullable=True)
    # Unique index handled separately
    checksum = Column(Text, nullable=False, unique=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=True)
    metadata_json = Column("metadata", JSONB, server_default="{}")
    model = Column(Text, nullable=False)
    vector = Column(Vector(dim=768), nullable=False)
