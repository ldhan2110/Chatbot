from pydantic_ai import Agent, ModelRetry, RunContext
from core.agents.knowledge_agent import knowledge_agent
from core.agents.sql_gen_agent import sql_gen_agent
from core.agents.deps.chat_deps import ChatDeps
from core.agents.deps.sql_deps import SqlDeps
from core.agents.deps.knowledge_deps import KnowledgeDeps
from core.agents.prompts.chat_prompt import chat_system_prompt
from core.utils.database import DatabaseTool, blueprint_db_engine
from core.utils.schema import format_sql_for_sqlalchemy
from settings import settings

chat_agent = Agent(
    # settings.get_model("ollama", 'PetrosStav/gemma3-tools:4b',
    #                    "http://localhost:11434/v1"),
    settings.get_model("google", 'gemini-2.5-flash'),
    deps_type=ChatDeps,
    output_type=str,
    retries=3
)


@chat_agent.instructions
async def chat_agent_instructions(ctx: RunContext[ChatDeps]) -> str:
    return chat_system_prompt.format(
        current_datetime=ctx.deps.current_datetime,
        today_date=ctx.deps.today_date,
    )


@chat_agent.tool(retries=5)
async def search_base_knowledge(ctx: RunContext[ChatDeps], nl_query: str):
    """Searching user prompt against our base knowledge"""
    try:
        print(f"[Tool] Searching against our base knowledge: {nl_query}")

        # Step 1: Ask the Knowledge agent to retrieve revelant doc chunk
        response = await knowledge_agent.run(nl_query, deps=KnowledgeDeps(ctx.deps))
        print(f"[Tool] Result: {response}")

    except Exception as ex:
        print(f"[chat_agent]: {ex}")
        raise ModelRetry(
            "Something went wrong")

    return response


@chat_agent.tool_plain(retries=5)
async def query_database_with_sql_agent(nl_query: str):
    """Convert NL to SQL via sql_agent and run it on the database."""
    try:
        print(f"[Tool] Converting NLP: {nl_query}")

        # Step 1: Ask the SQL agent to generate SQL
        sql_response = await sql_gen_agent.run(nl_query, deps=SqlDeps(engine=blueprint_db_engine.engine))
        sql = format_sql_for_sqlalchemy(sql_response.output.strip())
        print(f"[Tool] Converted SQL: {sql}")

        # Step 2: Run the SQL
        runner = DatabaseTool(blueprint_db_engine)
        result = runner.run(sql)
        print(result)
    except Exception as ex:
        print(f"[Tool] Execute SQL failed {ex}")
        raise ModelRetry(
            "The query 'bad' is not runnable. Please call the tool again to request it a different query.")

    return result
