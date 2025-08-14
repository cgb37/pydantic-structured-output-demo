"""Enhanced Pydantic schemas for structured LLM output."""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum
import uuid


class MessageRole(str, Enum):
    """Enumeration for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class LLMMessage(BaseModel):
    """Structured message for LLM interactions."""
    
    role: MessageRole
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate message content is not empty."""
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()


class ChatRequest(BaseModel):
    """Enhanced chat request with conversation context."""
    
    message: str = Field(..., min_length=1, description="User message")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for context")
    system_prompt: Optional[str] = Field(default=None, description="Optional system prompt")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4096)
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate user message."""
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class LLMMetadata(BaseModel):
    """Metadata about LLM generation."""
    
    model_name: str
    temperature: float
    tokens_used: Optional[int] = None
    generation_time_ms: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None


class ChatChoice(BaseModel):
    """A single chat completion choice."""
    
    message: LLMMessage
    finish_reason: Optional[Literal["stop", "length", "content_filter"]] = None
    index: int = Field(default=0, description="Choice index")


class ChatResponse(BaseModel):
    """Enhanced structured chat response."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: Optional[str] = None
    choices: List[ChatChoice]
    metadata: LLMMetadata
    created: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('choices')
    @classmethod
    def validate_choices(cls, v: List[ChatChoice]) -> List[ChatChoice]:
        """Validate at least one choice is provided."""
        if not v:
            raise ValueError('At least one choice must be provided')
        return v


class StructuredOutput(BaseModel):
    """Base class for structured output validation."""
    
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score for the output"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning or explanation for the output"
    )


class TaskAnalysis(StructuredOutput):
    """Structured analysis of a user task or question."""
    
    task_type: Literal["question", "request", "command", "creative", "analysis"]
    complexity: Literal["simple", "medium", "complex"]
    domain: str = Field(description="Subject domain or topic area")
    key_concepts: List[str] = Field(description="Key concepts identified")
    required_knowledge: List[str] = Field(description="Knowledge areas required")
    
    @field_validator('key_concepts', 'required_knowledge')
    @classmethod
    def validate_lists(cls, v: List[str]) -> List[str]:
        """Validate lists contain non-empty strings."""
        return [item.strip() for item in v if item.strip()]


class CodeAnalysis(StructuredOutput):
    """Structured analysis of code snippets."""
    
    language: str
    framework: Optional[str] = None
    patterns_used: List[str] = Field(default_factory=list)
    potential_issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    complexity_score: int = Field(ge=1, le=10, description="Code complexity (1-10)")


class ConversationContext(BaseModel):
    """Context for maintaining conversation state."""
    
    conversation_id: str
    messages: List[LLMMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def add_message(self, message: LLMMessage) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def get_recent_messages(self, limit: int = 10) -> List[LLMMessage]:
        """Get the most recent messages."""
        return self.messages[-limit:] if limit > 0 else self.messages
    
    def to_llm_format(self) -> List[Dict[str, str]]:
        """Convert to format expected by LLM."""
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in self.messages
        ]


class ErrorResponse(BaseModel):
    """Structured error response."""
    
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
