"""Service layer for LLM operations."""
import asyncio
import logging
from typing import Dict, Optional, List
from datetime import datetime
import json

from .client import LLMClient, LLMConfig
from .schemas import (
    ChatRequest,
    ChatResponse,
    ChatChoice,
    LLMMessage,
    LLMMetadata,
    ConversationContext,
    MessageRole,
    ErrorResponse
)

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation contexts and state."""
    
    def __init__(self):
        """Initialize the conversation manager."""
        self._conversations: Dict[str, ConversationContext] = {}
    
    def get_or_create_conversation(self, conversation_id: str) -> ConversationContext:
        """Get existing conversation or create new one."""
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = ConversationContext(
                conversation_id=conversation_id
            )
        return self._conversations[conversation_id]
    
    def add_message_to_conversation(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str
    ) -> None:
        """Add a message to a conversation."""
        conversation = self.get_or_create_conversation(conversation_id)
        message = LLMMessage(role=role, content=content)
        conversation.add_message(message)
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Get conversation history in LLM format."""
        if conversation_id not in self._conversations:
            return []
        
        conversation = self._conversations[conversation_id]
        return conversation.to_llm_format()[-limit:]
    
    def clear_conversation(self, conversation_id: str) -> None:
        """Clear a conversation."""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]


class LLMService:
    """High-level service for LLM operations."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize the LLM service."""
        self.config = config or LLMConfig()
        self.conversation_manager = ConversationManager()
        self._client: Optional[LLMClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
    
    async def _get_client(self) -> LLMClient:
        """Get or create LLM client."""
        if self._client is None:
            self._client = LLMClient(self.config)
        return self._client
    
    async def health_check(self) -> bool:
        """Check if the LLM service is healthy."""
        try:
            client = await self._get_client()
            return await client.health_check()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request and return structured response."""
        start_time = datetime.utcnow()
        
        try:
            # Get or create conversation context
            conversation_id = request.conversation_id or f"conv_{int(start_time.timestamp())}"
            
            # Add user message to conversation
            self.conversation_manager.add_message_to_conversation(
                conversation_id,
                MessageRole.USER,
                request.message
            )
            
            # Get conversation history for context
            messages = self.conversation_manager.get_conversation_history(
                conversation_id,
                limit=10
            )
            
            # Add system prompt if provided
            if request.system_prompt:
                messages.insert(0, {
                    "role": "system",
                    "content": request.system_prompt
                })
            
            # Generate response using LLM
            client = await self._get_client()
            response_content = await client.chat(
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            # Add assistant response to conversation
            self.conversation_manager.add_message_to_conversation(
                conversation_id,
                MessageRole.ASSISTANT,
                response_content
            )
            
            # Calculate generation time
            end_time = datetime.utcnow()
            generation_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Create structured response
            assistant_message = LLMMessage(
                role=MessageRole.ASSISTANT,
                content=response_content
            )
            
            choice = ChatChoice(
                message=assistant_message,
                finish_reason="stop"
            )
            
            metadata = LLMMetadata(
                model_name=self.config.model_name,
                temperature=request.temperature or self.config.temperature,
                generation_time_ms=generation_time_ms
            )
            
            return ChatResponse(
                conversation_id=conversation_id,
                choices=[choice],
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error processing chat request: {e}")
            raise
    
    async def analyze_user_input(self, user_input: str) -> Dict[str, str]:
        """Analyze user input to understand intent and context."""
        analysis_prompt = f"""
        Analyze the following user input and provide structured analysis:
        
        User Input: "{user_input}"
        
        Please analyze:
        1. Task type (question, request, command, creative, analysis)
        2. Complexity level (simple, medium, complex)
        3. Domain or subject area
        4. Key concepts mentioned
        5. Required knowledge areas
        
        Provide your analysis in a structured format.
        """
        
        try:
            client = await self._get_client()
            response = await client.generate(analysis_prompt)
            
            # For now, return simple analysis
            # In production, you might use structured output parsing
            return {
                "analysis": response,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing user input: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def generate_with_structured_output(
        self,
        prompt: str,
        output_schema: str,
        system_prompt: Optional[str] = None
    ) -> Dict:
        """Generate response with structured output format."""
        structured_prompt = f"""
        {system_prompt or "You are a helpful assistant."}
        
        Please respond to the following prompt with output structured according to the specified schema:
        
        Schema: {output_schema}
        
        Prompt: {prompt}
        
        Provide your response in valid JSON format that matches the schema.
        """
        
        try:
            client = await self._get_client()
            response = await client.generate(structured_prompt)
            
            # Try to parse as JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If not valid JSON, return wrapped response
                return {
                    "raw_response": response,
                    "parsed": False,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating structured output: {e}")
            raise
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self._client:
            await self._client.close()
            self._client = None
