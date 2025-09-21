from agents.chat.agent import chat_agent
from agents.chat.deps import ChatDeps

class ChatService:
    def __init__(self, thread_id: str) -> None:
        self.thread_id = thread_id
        self.chat_agent = chat_agent

    async def chat(self, prompt: str) -> str:
        result = await self.chat_agent.run(prompt, deps=ChatDeps())
        return result