"""Utility functions for LLM integration."""
import json
import re
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from text that might contain markdown or other formatting.
    
    Args:
        text: Text that might contain JSON
        
    Returns:
        Parsed JSON dictionary or None if no valid JSON found
    """
    # Try to find JSON code blocks first
    json_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(json_block_pattern, text, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue
    
    # Try to find JSON objects in the text
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, text)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # Try parsing the entire text as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None


def parse_structured_output(text: str, schema_class: Type[T]) -> Optional[T]:
    """Parse text into a Pydantic model instance.
    
    Args:
        text: Text to parse
        schema_class: Pydantic model class
        
    Returns:
        Validated model instance or None if parsing fails
    """
    try:
        # First try to extract JSON
        json_data = extract_json_from_text(text)
        if json_data is None:
            logger.warning(f"Could not extract JSON from text: {text[:100]}...")
            return None
        
        # Validate with Pydantic model
        return schema_class(**json_data)
        
    except ValidationError as e:
        logger.error(f"Validation error parsing {schema_class.__name__}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing structured output: {e}")
        return None


def clean_text_content(text: str) -> str:
    """Clean and normalize text content.
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common markdown artifacts that might interfere
    text = re.sub(r'^```.*?\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    
    return text


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append when truncating
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    # Try to truncate at word boundary
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # Only use word boundary if it's not too early
        truncated = truncated[:last_space]
    
    return truncated + suffix


def format_conversation_for_llm(
    messages: list,
    max_context_length: int = 4000
) -> list:
    """Format conversation messages for LLM context.
    
    Args:
        messages: List of message dictionaries
        max_context_length: Maximum total character length for context
        
    Returns:
        Formatted and potentially truncated message list
    """
    if not messages:
        return []
    
    # Calculate total length
    total_length = sum(len(msg.get('content', '')) for msg in messages)
    
    if total_length <= max_context_length:
        return messages
    
    # Keep system message and recent messages that fit in context
    formatted_messages = []
    current_length = 0
    
    # Always keep system message if present
    if messages and messages[0].get('role') == 'system':
        formatted_messages.append(messages[0])
        current_length += len(messages[0].get('content', ''))
    
    # Add messages from the end (most recent) while staying under limit
    for msg in reversed(messages[1:] if formatted_messages else messages):
        msg_length = len(msg.get('content', ''))
        if current_length + msg_length <= max_context_length:
            formatted_messages.insert(-1 if formatted_messages else 0, msg)
            current_length += msg_length
        else:
            break
    
    return formatted_messages


def validate_llm_response(response: str, expected_format: str = "text") -> bool:
    """Validate LLM response format.
    
    Args:
        response: LLM response text
        expected_format: Expected format ("text", "json", "structured")
        
    Returns:
        True if response is valid for expected format
    """
    if not response or not response.strip():
        return False
    
    if expected_format == "text":
        return True
    elif expected_format == "json":
        return extract_json_from_text(response) is not None
    elif expected_format == "structured":
        # Check if response contains structured elements
        return bool(re.search(r'\{.*\}', response, re.DOTALL))
    
    return False


def create_error_response(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized error response.
    
    Args:
        error_type: Type of error
        message: Error message
        details: Additional error details
        
    Returns:
        Error response dictionary
    """
    from datetime import datetime
    
    return {
        "error": True,
        "error_type": error_type,
        "message": message,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat()
    }


def estimate_tokens(text: str) -> int:
    """Rough estimation of token count for text.
    
    Args:
        text: Text to estimate tokens for
        
    Returns:
        Estimated token count
    """
    # Very rough estimation: ~4 characters per token on average
    return max(1, len(text) // 4)


def prepare_system_prompt(
    base_prompt: str,
    additional_context: Optional[str] = None,
    output_format: Optional[str] = None
) -> str:
    """Prepare system prompt with context and formatting instructions.
    
    Args:
        base_prompt: Base system prompt
        additional_context: Additional context to include
        output_format: Specific output format instructions
        
    Returns:
        Complete system prompt
    """
    prompt_parts = [base_prompt]
    
    if additional_context:
        prompt_parts.append(f"\nAdditional Context: {additional_context}")
    
    if output_format:
        prompt_parts.append(f"\nOutput Format: {output_format}")
    
    return "\n".join(prompt_parts)
