from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from models.prompt import Conversation
from router import chat_router
from services.chat import ChatService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Protected routes
app.include_router(chat_router.router)

@app.get("/chat/stream")
async def chat(prompt: str) -> StreamingResponse:
    chat_service = ChatService(thread_id=1)
    return await chat_service.chat_stream(prompt=prompt)
