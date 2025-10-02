from fastapi.responses import StreamingResponse
from pydantic_core import to_jsonable_python
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.models import ChatRequest, ChatResponse
from core.agents.deps.chat_deps import ChatDeps
from core.agents.chat_agent import chat_agent
from core.repositories.conversation import ConversationRepository
from core.utils.streaming import format_sse, stream_agent_text


class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chat_agent = chat_agent
        self.conversation_repo = ConversationRepository(session)

    # Load Short-term memory
    async def load_message_history(self, conversation_id) -> list[ModelMessage]:
        message_history: list[ModelMessage] = []
        try:
            runs = await self.conversation_repo.list_message_runs(conversation_id)
            for r in runs:
                msgs = ModelMessagesTypeAdapter.validate_python(r.messages)
                message_history.extend(msgs)
        except Exception as ex:
            raise Exception(f"Failed to load history message: {ex}")
        return message_history

    async def chat(self, payload: ChatRequest) -> ChatResponse:
        try:
            conversation = None

            if payload.conversation_id is not None:
                conversation = await self.conversation_repo.getConversation(payload.conversation_id)

            if conversation is None:
                conversation = await self.conversation_repo.create(title="Default Chat", owner="admin")

            # Load message history
            message_history = await self.load_message_history(conversation.conversation_id)

            result = await self.chat_agent.run(
                user_prompt=payload.message,
                message_history=message_history,
                deps=ChatDeps()
            )

            # Persist new messages to DB
            messages = ModelMessagesTypeAdapter.validate_python(
                result.new_messages())
            jsonable_msgs = to_jsonable_python(
                messages, bytes_mode="base64")
            await self.conversation_repo.persist_message_run(conversation, jsonable_msgs, 'admin')

            # Commit the result
            await self.session.commit()
        except Exception as ex:
            await self.session.rollback()
            raise ex

        return ChatResponse(conversation_id=conversation.conversation_id, assistant_prompt=result.output)

    async def chat_stream(self, payload: ChatRequest) -> StreamingResponse:
        async def stream_generator():
            conversation = None
            created_new_conversation = False

            if payload.conversation_id is not None:
                conversation = await self.conversation_repo.getConversation(payload.conversation_id)

            if conversation is None:
                conversation = await self.conversation_repo.create(title="Default Chat", owner="admin")
                created_new_conversation = True

            if created_new_conversation:
                evt_payload = {"conversation_id": str(
                    conversation.conversation_id)}
                yield format_sse("conversation_created", evt_payload)

            # Load message history
            message_history = await self.load_message_history(conversation.conversation_id)

            # # Decode media and build user content
            # safe_media = chat_service.decode_media_items(payload.media)
            # user_prompt = [payload.message, *safe_media]

            # On Complete Handler
            async def on_complete(result) -> list[str]:
                events: list[str] = []
                try:
                    messages = ModelMessagesTypeAdapter.validate_python(
                        result.new_messages())
                    jsonable_msgs = to_jsonable_python(
                        messages, bytes_mode="base64")
                    await self.conversation_repo.persist_message_run(conversation, jsonable_msgs, 'admin')

                    try:
                        await self.session.commit()
                    except Exception:
                        raise Exception(
                            "Failed to commit session after run persistence")
                except Exception as ex:
                    raise Exception(f"Something went wrong: {ex}")

                # Append Done event to end stream
                events.append(format_sse("done", "[DONE]"))
                return events

            try:
                async for sse_message in stream_agent_text(
                    self.chat_agent,
                    user_prompt=payload.message,
                    model_name=self.chat_agent.model.model_name,
                    deps=ChatDeps(),
                    message_history=message_history,
                    on_complete=on_complete
                ):
                    yield sse_message
            except Exception as exc:
                error_response = {
                    "error": "Chat execution error",
                    "error_type": type(exc).__name__,
                    "details": str(exc),
                }
                yield format_sse("error", error_response)

        # Return Stream result
        return StreamingResponse(stream_generator(), media_type="text/event-stream; charset=utf-8")
