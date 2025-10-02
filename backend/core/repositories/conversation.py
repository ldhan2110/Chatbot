from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.db_models import Conversation, ConversationMessageRun


class ConversationRepository():
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def getConversation(self, id: UUID) -> Conversation:
        return await self.session.get(Conversation, id)

    async def list_message_runs(self, conversation_id: UUID) -> list[ConversationMessageRun]:
        stmt = (
            select(ConversationMessageRun)
            .where(ConversationMessageRun.conversation_id == conversation_id)
            .order_by(ConversationMessageRun.cre_dt.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, title: str, owner: str) -> Conversation:
        try:
            conversation = Conversation(
                title=title, upd_usr_id=owner, cre_usr_id=owner)
            self.session.add(conversation)
            await self.session.flush()
            return conversation
        except Exception as ex:
            await self.session.rollback()
            print(
                f"[ConversationRepository][create] Failed to create conversation: {ex}")

    # Conversation message runs

    async def persist_message_run(self, conversation: Conversation, messages_obj: dict | list, owner: str) -> ConversationMessageRun:
        run = ConversationMessageRun(
            conversation_id=conversation.conversation_id,
            messages=messages_obj,
            cre_usr_id=owner,
            upd_usr_id=owner
        )
        self.session.add(run)
        await self.session.flush()
        await self.session.refresh(run)
        return run
