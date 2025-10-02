from pydantic_ai import Agent, RunContext
from core.agents.deps.sql_deps import SqlDeps
from core.agents.prompts.sql_gen_prompt import sql_gen_system_prompt
from settings import settings

sql_gen_agent = Agent(
    settings.get_model("google", 'gemini-2.5-flash'),
    deps_type=SqlDeps,
    output_type=str,
    retries=3
)


@sql_gen_agent.instructions
async def sql_agent_instruction(ctx: RunContext[SqlDeps]) -> str:
    return sql_gen_system_prompt.format(
        current_datetime=ctx.deps.current_datetime,
        today_date=ctx.deps.today_date,
        schema_ctx=ctx.deps.schema_ctx
    )
