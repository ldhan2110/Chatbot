from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.router.chat_router import chat_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        'https://localhost:8443'
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Protected routes
app.include_router(chat_router)
