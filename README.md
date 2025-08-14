# Pydantic Structured Output Demo with LLM Integration

A demo project showcasing **Pydantic structured output** with a modular Quart web application, now integrated with **gpt-oss:20b** for real-world LLM interactions and validation.

## Features

- 🤖 **LLM Integration**: Connect to gpt-oss:20b running locally on your Mac M1
- 📝 **Pydantic Validation**: Structured input/output validation with detailed error handling  
- 💬 **Conversational AI**: Maintain conversation context across multiple messages
- 🏗️ **Modular Architecture**: Clean, DRY code with atomized functions and utilities
- 🚀 **Production Ready**: Proper error handling, logging, and health checks
- 📊 **Multiple Output Formats**: Support for text, JSON, and structured Pydantic outputs

## Quick Start

### Prerequisites

1. **Install and run gpt-oss:20b with Ollama**:
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull and run the model
   ollama pull gpt-oss:20b
   ollama serve  # Keep this running
   ```

2. **Verify the model is available**:
   ```bash
   ollama list  # Should show gpt-oss:20b
   ```

### Running the Application

#### Option 1: Docker (Recommended)
```bash
docker compose up --build
```

#### Option 2: Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Test LLM connection first
python test_llm.py

# Run the application
python app.py
```

Visit **http://localhost:8001** for the chat UI and **http://localhost:8001/api/health** for health checks.

## API Endpoints

### Chat Endpoints
- `POST /api/chat` - Enhanced chat with LLM integration and structured output
- `POST /api/chat/legacy` - Simple echo endpoint for testing
- `GET /api/health` - Health check including LLM service status

### Advanced Features
- `POST /api/analyze` - Analyze user input for intent and structure
- `POST /api/structured-output` - Generate responses following specific JSON schemas

### Example API Usage

```bash
# Basic chat
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain Pydantic validation", "temperature": 0.7}'

# Structured output
curl -X POST http://localhost:8001/api/structured-output \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze this Python code for issues",
    "schema": {"type": "object", "properties": {"issues": {"type": "array"}}},
    "system_prompt": "You are a code review expert"
  }'
```

## Project Structure

```
├── app.py                          # Application entry point
├── webapp/                         # Main application package
│   ├── __init__.py                # App factory
│   ├── config.py                  # Configuration
│   ├── schemas.py                 # Legacy Pydantic schemas
│   ├── llm/                       # LLM integration module
│   │   ├── __init__.py           # Module exports
│   │   ├── client.py             # HTTP client for LLM API
│   │   ├── service.py            # Business logic layer
│   │   ├── schemas.py            # Enhanced Pydantic models
│   │   └── utils.py              # Utility functions
│   ├── api/                      # API blueprint
│   │   └── routes.py             # API endpoints
│   └── home/                     # Web UI blueprint
│       └── routes.py             # UI routes
├── templates/                     # Jinja2 templates
├── static/                       # Static assets (CSS, JS)
├── examples/                     # Usage examples
│   ├── llm_examples.py          # LLM integration examples
│   └── llm_config.py            # Configuration examples
├── tests/                        # Test suite
└── test_llm.py                   # LLM connection test script
```

## Key Features Demonstrated

### 1. Pydantic Validation
```python
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()
```

### 2. Structured Output Generation
The system can generate and validate structured responses following specific schemas:

```python
# Request structured output
result = await service.generate_with_structured_output(
    prompt="Analyze this task",
    output_schema=task_schema,
    system_prompt="You are an expert analyzer"
)

# Validate with Pydantic
validated_result = TaskAnalysis(**result)
```

### 3. Conversation Context
Maintains conversation state across multiple exchanges:

```python
# Conversation context is automatically maintained
request1 = ChatRequest(message="I'm building a web app", conversation_id="conv_123")
request2 = ChatRequest(message="How should I structure it?", conversation_id="conv_123")
```

## Testing

Run the full test suite:
```bash
pytest -v
```

Test just the LLM integration:
```bash
python test_llm.py
```

Run specific examples:
```bash
python examples/llm_examples.py
```

## Configuration

Configure the LLM connection via environment variables:

```bash
export LLM_BASE_URL="http://localhost:11434"
export LLM_MODEL_NAME="gpt-oss:20b"
export LLM_TIMEOUT="60.0"
export LLM_TEMPERATURE="0.7"
export LLM_MAX_TOKENS="2048"
```

## Troubleshooting

### LLM Connection Issues
1. Ensure Ollama is running: `ollama serve`
2. Verify model is available: `ollama list`
3. Check service health: `curl http://localhost:8001/api/health`
4. Test connection: `python test_llm.py`

### Performance on Mac M1
- The 20B model is large; expect slower responses on some systems
- Monitor memory usage during operation
- Consider GPU acceleration if available

### Common Issues
- **Port conflicts**: Change port in `app.py` if 8001 is in use
- **Memory errors**: The 20B model requires significant RAM
- **Timeout errors**: Increase timeout settings for slower responses

## Development

This project demonstrates best practices for:
- **Clean Architecture**: Separation of concerns with service layers
- **Type Safety**: Full Pydantic validation throughout
- **Error Handling**: Comprehensive error handling and user feedback
- **Async Programming**: Proper async/await usage with Quart
- **Testing**: Unit tests and integration tests
- **Documentation**: Clear examples and usage patterns

## License

MIT License - feel free to use this as a starting point for your own projects!
