"""LLM client for interacting with gpt-oss:latest model."""
import httpx
import json
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, field_validator
import logging

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """Configuration for LLM client."""
    
    base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    model_name: str = os.getenv("LLM_MODEL_NAME", "gpt-oss:latest")
    timeout: float = float(os.getenv("LLM_TIMEOUT", "300.0"))
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    
    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('base_url must start with http:// or https://')
        return v.rstrip('/')


class LLMClient:
    """Client for interacting with the local gpt-oss:latest model."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize the LLM client with configuration."""
        self.config = config or LLMConfig()
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.timeout)
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using the LLM.
        
        Args:
            prompt: User prompt text
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
            
        Raises:
            httpx.HTTPError: If API call fails
            ValueError: If response format is invalid
        """
        payload = self._build_payload(prompt, system_prompt, **kwargs)
        
        try:
            response = await self._client.post(
                f"{self.config.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            # Parse streaming response if needed
            if response.headers.get('content-type', '').startswith('application/x-ndjson'):
                return self._parse_streaming_response(response.text)
            
            result = response.json()
            return result.get('response', '')
            
        except httpx.HTTPError as e:
            logger.error(f"LLM API error: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise ValueError("Invalid response format from LLM")
    
    async def chat(
        self,
        messages: list[dict],
        **kwargs
    ) -> str:
        """Chat with the LLM using message history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response text
        """
        payload = self._build_chat_payload(messages, **kwargs)
        
        try:
            response = await self._client.post(
                f"{self.config.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('message', {}).get('content', '')
            
        except httpx.HTTPError as e:
            logger.error(f"LLM chat API error: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM chat response: {e}")
            raise ValueError("Invalid response format from LLM")
    
    def _build_payload(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build request payload for generation."""
        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', self.config.temperature),
            }
        }
        
        if self.config.max_tokens:
            payload["options"]["num_predict"] = self.config.max_tokens
        
        if system_prompt:
            payload["system"] = system_prompt
            
        return payload
    
    def _build_chat_payload(
        self,
        messages: list[dict],
        **kwargs
    ) -> Dict[str, Any]:
        """Build request payload for chat."""
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', self.config.temperature),
            }
        }
        
        if self.config.max_tokens:
            payload["options"]["num_predict"] = self.config.max_tokens
            
        return payload
    
    def _parse_streaming_response(self, response_text: str) -> str:
        """Parse streaming NDJSON response."""
        lines = response_text.strip().split('\n')
        content_parts = []
        
        for line in lines:
            if line:
                try:
                    data = json.loads(line)
                    if 'response' in data:
                        content_parts.append(data['response'])
                except json.JSONDecodeError:
                    continue
        
        return ''.join(content_parts)
    
    async def health_check(self) -> bool:
        """Check if the LLM service is healthy."""
        try:
            response = await self._client.get(f"{self.config.base_url}/api/tags")
            response.raise_for_status()
            
            # Check if our model is available
            result = response.json()
            models = [model.get('name', '') for model in result.get('models', [])]
            return self.config.model_name in models
            
        except (httpx.HTTPError, json.JSONDecodeError):
            return False
