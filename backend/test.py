import asyncio
import requests
from pydantic_ai import Agent, RunContext
from core.utils.database import db_chatbot_runner
from settings import settings

# -----------------------------
# Agent setup
# -----------------------------
knowledge_agent = Agent(
    settings.get_model("ollama", "llama3:8b", "http://localhost:11434/v1"),
    deps_type=str,
    output_type=str,
    system_prompt="""
        You are a specialized Vector DB agent.
        Whenever a user asks a question, you must call the tool `search_similar_chunks(user_prompt, top_k)`
    """
)

# -----------------------------
# Tool definition
# -----------------------------


@knowledge_agent.tool
async def search_similar_chunks(ctx: RunContext, user_prompt: str, top_k: int = 5):
    """
    Query the vector database with a user prompt.
    Returns the top_k most similar chunks from embeddings table.
    """
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
        rows = await db_chatbot_runner.run(
            sql, {"embedding": embedding_str, "top_k": top_k})

        print(rows)

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

        return {"results": results}

    except Exception as e:
        print("DB query error:", e)
        return {"error": f"Vector DB query failed: {str(e)}"}

# -----------------------------
# Async example usage
# -----------------------------


async def main():
    result = await knowledge_agent.run(user_prompt="What is Mr. Lee Moon Young Jobs ?", deps="")
    print(result)

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
