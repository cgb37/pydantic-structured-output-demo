from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    message: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatResponse(BaseModel):
    id: str
    model: str
    choices: List[ChatMessage]
