from fastapi import FastAPI
from models.prompt import Prompt
from services.chat import ChatService

app = FastAPI()

@app.post("/chat")
async def chat(prompt: Prompt) -> str:
    chat_service = ChatService(thread_id=1)
    result = await chat_service.chat(prompt.prompt)
    return result.output