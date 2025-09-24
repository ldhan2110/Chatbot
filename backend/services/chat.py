
from fastapi.responses import StreamingResponse
from agents.chat.agent import chat_agent
from agents.chat.deps import ChatDeps
from services.streaming import format_sse, stream_agent_text
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.conversation import ConversationRepository

class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.conversation_repo = ConversationRepository(session)
        self.chat_agent = chat_agent

    async def chat_stream(self, prompt: str) -> StreamingResponse:
        async def stream_generator():
            try:
                async for sse_message in stream_agent_text(
                    self.chat_agent,
                    prompt,
                    deps=ChatDeps(),
                ):
                    yield sse_message
                yield format_sse("done", "[DONE]")
            except Exception as exc:
                error_response = {
                    "error": "Chat execution error",
                    "error_type": type(exc).__name__,
                    "details": str(exc),
                }
                yield format_sse("error", error_response)
        return StreamingResponse(stream_generator(), media_type="text/event-stream; charset=utf-8")
