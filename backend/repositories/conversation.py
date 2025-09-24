from sqlalchemy.ext.asyncio import AsyncSession
from repositories.models.models import Conversation
from uuid import UUID


class ConversationRepository():
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def getConversation(self, id: UUID) -> Conversation:
        return await self.session.get(Conversation, id);

    async def addConversation(self, entity: Conversation) -> None:
        try:
            self.session.add(entity)
            await self.session.flush()
            await self.session.commit()
            return entity
        except Exception as ex:
            await self.session.rollback()
            print(f"Something went wrong: {ex}")