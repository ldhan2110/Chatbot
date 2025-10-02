
import json
from typing import Any, AsyncGenerator, Awaitable, Callable, Optional
from settings import settings
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelMessage,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    TextPart,
    ToolReturnPart,
)


def extract_tool_return_parts(
    messages: list[ModelMessage],
    tool_name: str,
) -> list[ToolReturnPart]:
    tool_return_parts: list[ToolReturnPart] = []
    for message in messages:
        for part in message.parts:
            if isinstance(part, ToolReturnPart) and part.tool_name == tool_name:
                tool_return_parts.append(part)
    return tool_return_parts


def format_sse(event: str, data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


def extract_tool_call(messages: list[ModelMessage], tool_name: str) -> list[dict]:
    search_results: list[dict] = []
    seen_urls: set[str] = set()

    tool_return_parts = extract_tool_return_parts(messages, tool_name)
    if tool_return_parts:
        for tool_return_part in tool_return_parts:
            content = (
                tool_return_part.get("content")
                if isinstance(tool_return_part, dict)
                else getattr(tool_return_part, "content", None)
            )
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        url = item.get("url")
                        if isinstance(url, str) and url in seen_urls:
                            continue
                        if isinstance(url, str):
                            seen_urls.add(url)
                            search_results.append(item)
    return search_results


async def stream_agent_text(
    agent: Agent,
    user_prompt: Any,
    model_name: str | None,
    *,
    deps: Any,
    message_history: Optional[list[ModelMessage]] = None,
    on_complete: Optional[Callable[[Any], Awaitable[list[str]]]] = None,
) -> AsyncGenerator[str, None]:
    """Stream assistant text as SSE messages and optionally run completion hook.
    Parameters
    - agent: pydantic-ai Agent-like object exposing run_stream(...)
    - user_prompt: string | list[BinaryContent | str]
    - deps: dependency object passed to the agent
    - message_history: prior ModelMessage list
    - on_complete: async callback receiving the run result; returns extra SSE events
    """
    messages: list[ModelMessage] = []

    dup_msg: str = ""

    async with agent.iter(user_prompt,
                          deps=deps,
                          message_history=message_history) as run:
        async for node in run:
            if Agent.is_call_tools_node(node):
                messages.append(node.model_response)
                if node.model_response is not None:
                    for part in node.model_response.parts:
                        if isinstance(part, TextPart):
                            yield format_sse(
                                "ai_message",
                                {
                                    "chunk": {"content": part.content},
                                    "model": model_name,
                                },
                            )
                            dup_msg = part.content
                async with node.stream(run.ctx) as handle_stream:
                    async for event in handle_stream:
                        if isinstance(event, FunctionToolCallEvent):
                            yield format_sse(
                                "ai_message",
                                {
                                    "tool_call": {"content": f"Calling Tool {event.part.tool_name!r} with args {event.part.args}"},
                                    "model": model_name,
                                },
                            )

                        elif isinstance(event, FunctionToolResultEvent):
                            print(
                                f"[Tool Call Result]: {event.result.content}")
            elif Agent.is_model_request_node(node):
                messages.append(node.request)
            elif Agent.is_end_node(node):
                if (dup_msg != node.data.output and dup_msg != ""):
                    yield format_sse(
                        "ai_message",
                        {
                            "chunk": {"content": node.data.output},
                            "model": model_name,
                        },
                    )

        if run.result:
            if on_complete is not None:
                try:
                    extra_events = await on_complete(run.result)
                    for evt in extra_events:
                        yield evt
                except Exception:
                    # Swallow completion hook errors to avoid breaking the stream termination
                    # Logging is left to the caller where session context is available
                    pass


__all__ = ["format_sse", "stream_agent_text", "extract_tool_call"]
