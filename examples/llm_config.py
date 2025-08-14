"""
Configuration for gpt-oss:20b integration.

Adjust these settings based on your local setup.
"""
import os
from webapp.llm import LLMConfig

# Default configuration for local gpt-oss:20b
# Assuming you're running it with Ollama or similar tool
DEFAULT_LLM_CONFIG = LLMConfig(
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434"),
    model_name=os.getenv("LLM_MODEL_NAME", "gpt-oss:20b"),
    timeout=float(os.getenv("LLM_TIMEOUT", "60.0")),  # Increased timeout for 20B model
    temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
    max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2048")) if os.getenv("LLM_MAX_TOKENS") else None
)

# System prompts for different use cases
SYSTEM_PROMPTS = {
    "default": """You are a helpful AI assistant. Provide clear, accurate, and informative responses. 
When asked to provide structured output, follow the specified format exactly.""",
    
    "code_analysis": """You are an expert software engineer. Analyze code carefully and provide 
structured feedback including patterns, potential issues, and suggestions for improvement.""",
    
    "task_analysis": """You are an expert task analyzer. Break down user requests into structured 
components including task type, complexity, domain, and required knowledge areas.""",
    
    "pydantic_demo": """You are demonstrating Pydantic structured output capabilities. 
Always provide responses that showcase how Pydantic can validate and structure data effectively. 
Include examples and explain the benefits of type validation."""
}

# Example schemas for structured output
EXAMPLE_SCHEMAS = {
    "task_analysis": {
        "type": "object",
        "properties": {
            "task_type": {
                "type": "string", 
                "enum": ["question", "request", "command", "creative", "analysis"],
                "description": "Type of task requested"
            },
            "complexity": {
                "type": "string", 
                "enum": ["simple", "medium", "complex"],
                "description": "Estimated complexity level"
            },
            "domain": {
                "type": "string",
                "description": "Subject domain or area"
            },
            "key_concepts": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Key concepts identified in the request"
            },
            "estimated_time": {
                "type": "string",
                "description": "Estimated time to complete"
            },
            "confidence_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Confidence in the analysis"
            }
        },
        "required": ["task_type", "complexity", "domain", "key_concepts"]
    },
    
    "code_review": {
        "type": "object",
        "properties": {
            "language": {"type": "string"},
            "framework": {"type": "string"},
            "patterns_identified": {
                "type": "array",
                "items": {"type": "string"}
            },
            "strengths": {
                "type": "array",
                "items": {"type": "string"}
            },
            "issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                        "description": {"type": "string"},
                        "suggestion": {"type": "string"}
                    }
                }
            },
            "overall_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 10
            }
        }
    }
}

# Tips for using gpt-oss:20b effectively
USAGE_TIPS = """
Tips for using gpt-oss:20b with this demo:

1. Model Setup:
   - Make sure you have gpt-oss:20b pulled in Ollama: `ollama pull gpt-oss:20b`
   - Start Ollama server: `ollama serve`
   - Verify model is available: `ollama list`

2. Performance:
   - The 20B model is quite large and may be slow on some machines
   - Consider using a GPU if available
   - Adjust timeout settings in configuration if needed

3. Structured Output:
   - Use specific prompts that request JSON format
   - Provide clear schemas for best results
   - Validate output with Pydantic models

4. Memory Usage:
   - Monitor system memory when running the 20B model
   - Consider using smaller models for development/testing

5. Troubleshooting:
   - Check Ollama logs if the service seems unresponsive
   - Restart Ollama if you encounter connection issues
   - Use the /api/health endpoint to check service status
"""
