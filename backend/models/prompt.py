from pydantic import BaseModel

class Prompt(BaseModel):
    prompt: str | None

class Conversation(BaseModel):
    title: str