from pydantic import BaseModel, field_validator
from typing import List, Literal


class ChatRequest(BaseModel):
    message: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatResponse(BaseModel):
    id: str
    model: str
    choices: List[ChatMessage]
