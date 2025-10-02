from typing import Any
import requests
from core.models.models import RevelantDocChunk
from settings import settings
from pydantic_ai import Agent, ModelSettings, RunContext
from core.agents.prompts.vectordb_prompt import vector_db_system_prompt
from core.agents.deps.knowledge_deps import KnowledgeDeps
from core.utils.database import AsyncDatabaseTool, chatbot_db_engine

knowledge_agent = Agent(
    # settings.get_model("ollama", 'PetrosStav/gemma3-tools:4b',
    #                    "http://localhost:11434/v1"),
    settings.get_model("google", 'gemini-2.5-flash'),
    deps_type=KnowledgeDeps,
    output_type=str,
    model_settings=ModelSettings(
        tool_choice={
            "type": "function",
            "function": {"name": "search_base_knowledge"}
        }
    )
)


@knowledge_agent.instructions
async def knowledge_agent_instruction(ctx: RunContext[KnowledgeDeps]) -> str:
    return vector_db_system_prompt.format(
        current_datetime=ctx.deps.current_datetime,
        today_date=ctx.deps.today_date
    )


@knowledge_agent.tool
async def search_similar_chunks(ctx: RunContext[None], user_prompt: str, top_k: int = 5):
    """
    Query the vector database with a user prompt.
    Returns the top_k most similar chunks from embeddings table.
    """
    print(f"[Tools]: Calling base knowledge tool.")
    # 1️⃣ Generate embedding via Ollama
    try:
        url = "http://localhost:11434/api/embeddings"
        payload = {"model": "nomic-embed-text", "prompt": user_prompt}
        r = requests.post(url, json=payload)
        r.raise_for_status()
        embedding = r.json()["embedding"]
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
    except Exception as e:
        print("Embedding Error:", e)
        return {"error": f"Failed to generate embedding: {str(e)}"}

    # 2️⃣ Query vector DB safely using parameters
    try:
        sql = """
            SELECT e.chunk_id, e.model, e.text, e.vector, e.metadata,
                   e.vector <#> :embedding AS similarity
            FROM doc_chunks e
            ORDER BY similarity
            LIMIT :top_k
        """

        db_chatbot_runner = AsyncDatabaseTool(chatbot_db_engine)
        rows = await db_chatbot_runner.run(
            sql, {"embedding": embedding_str, "top_k": top_k})

        # 3️⃣ Format structured JSON results
        results = []
        for r in rows:
            results.append({
                "chunk_id": r["chunk_id"],
                "model": r["model"],
                "vector": list(r["vector"]),  # convert pgvector to list
                "metadata": r["metadata"],
                "similarity_score": r["similarity"]
            })

        return results

    except Exception as e:
        print("DB query error:", e)
        return {"error": f"Vector DB query failed: {str(e)}"}
