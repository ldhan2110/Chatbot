from agents.chat.deps import ChatDeps
from agents.chat.prompts import system_prompt
from pydantic_ai import Agent, RunContext
from settings import settings 

chat_agent = Agent(
    settings.model,
    deps_type=ChatDeps,
    output_type=str,
    retries=3,
)

@chat_agent.instructions
async def chat_agent_instructions(ctx: RunContext[ChatDeps]) -> str:
    return system_prompt.format(
        current_datetime=ctx.deps.current_datetime,
        today_date=ctx.deps.today_date,
    )

if __name__ == "__main__":
    import asyncio

    response = asyncio.run(
        chat_agent.run(
            "Tường tận chi tiết về tiểu sử của đồng chí Tô Lâm",
            deps=ChatDeps(),
        )
    )

    print(response.all_messages())
