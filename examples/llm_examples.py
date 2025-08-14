"""
Example usage of the LLM integration with structured output.

This script demonstrates how to use the LLM service directly
and shows various Pydantic structured output features.
"""
import asyncio
import json
from pathlib import Path
import sys

# Add the webapp to the path so we can import it
sys.path.append(str(Path(__file__).parent.parent))

from webapp.llm import LLMService, ChatRequest, TaskAnalysis, CodeAnalysis
from webapp.llm.utils import parse_structured_output


async def basic_chat_example():
    """Basic chat example with conversation context."""
    print("=== Basic Chat Example ===")
    
    async with LLMService() as service:
        # Check service health
        if not await service.health_check():
            print("❌ LLM service is not available. Make sure gpt-oss:20b is running.")
            return
        
        # Create chat request
        request = ChatRequest(
            message="Hello! Can you explain what Pydantic is and why it's useful?",
            temperature=0.7
        )
        
        # Get response
        response = await service.process_chat_request(request)
        
        print(f"Model: {response.metadata.model_name}")
        print(f"Response time: {response.metadata.generation_time_ms}ms")
        print(f"Assistant: {response.choices[0].message.content}")


async def structured_output_example():
    """Example of generating structured output with a specific schema."""
    print("\n=== Structured Output Example ===")
    
    service = LLMService()
    
    try:
        if not await service.health_check():
            print("❌ LLM service is not available.")
            return
        
        # Define a schema for task analysis
        schema = {
            "type": "object",
            "properties": {
                "task_type": {"type": "string", "enum": ["question", "request", "command", "creative", "analysis"]},
                "complexity": {"type": "string", "enum": ["simple", "medium", "complex"]},
                "domain": {"type": "string"},
                "key_concepts": {"type": "array", "items": {"type": "string"}},
                "required_knowledge": {"type": "array", "items": {"type": "string"}},
                "confidence_score": {"type": "number", "minimum": 0, "maximum": 1}
            }
        }
        
        # Generate structured output
        result = await service.generate_with_structured_output(
            prompt="I want to build a REST API using FastAPI with PostgreSQL database integration",
            output_schema=json.dumps(schema),
            system_prompt="You are an expert software architect. Analyze the user's request and provide structured analysis."
        )
        
        print("Structured Output:")
        print(json.dumps(result, indent=2))
        
        # Try to parse into Pydantic model
        if isinstance(result, dict) and result.get('parsed') != False:
            task_analysis = parse_structured_output(json.dumps(result), TaskAnalysis)
            if task_analysis:
                print("\nParsed into Pydantic model:")
                print(f"Task Type: {task_analysis.task_type}")
                print(f"Complexity: {task_analysis.complexity}")
                print(f"Domain: {task_analysis.domain}")
                print(f"Key Concepts: {', '.join(task_analysis.key_concepts)}")
    
    finally:
        await service.cleanup()


async def conversation_context_example():
    """Example showing conversation context maintenance."""
    print("\n=== Conversation Context Example ===")
    
    service = LLMService()
    
    try:
        if not await service.health_check():
            print("❌ LLM service is not available.")
            return
        
        conversation_id = "demo_conversation"
        
        # First message
        request1 = ChatRequest(
            message="I'm working on a Python web application with FastAPI.",
            conversation_id=conversation_id
        )
        response1 = await service.process_chat_request(request1)
        print(f"User: {request1.message}")
        print(f"Assistant: {response1.choices[0].message.content}")
        
        # Follow-up message that references previous context
        request2 = ChatRequest(
            message="How should I structure the database models for this project?",
            conversation_id=conversation_id
        )
        response2 = await service.process_chat_request(request2)
        print(f"\nUser: {request2.message}")
        print(f"Assistant: {response2.choices[0].message.content}")
        
        # Show conversation history
        history = service.conversation_manager.get_conversation_history(conversation_id)
        print(f"\nConversation History ({len(history)} messages):")
        for msg in history:
            print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    finally:
        await service.cleanup()


async def error_handling_example():
    """Example showing error handling and validation."""
    print("\n=== Error Handling Example ===")
    
    service = LLMService()
    
    try:
        # Test with invalid request
        try:
            request = ChatRequest(
                message="",  # Empty message should fail validation
                temperature=3.0  # Invalid temperature should fail validation
            )
        except Exception as e:
            print(f"✅ Validation error caught: {e}")
        
        # Test with valid request but simulate service failure
        # (This would normally work if the service is available)
        print("Testing with valid request...")
        request = ChatRequest(
            message="This is a test message",
            temperature=0.5
        )
        print(f"✅ Valid request created: {request.message}")
    
    finally:
        await service.cleanup()


async def main():
    """Run all examples."""
    print("🚀 LLM Integration Examples")
    print("=" * 50)
    
    await basic_chat_example()
    await structured_output_example()
    await conversation_context_example()
    await error_handling_example()
    
    print("\n✨ Examples completed!")
    print("\nTo test the web interface:")
    print("1. Make sure gpt-oss:20b is running on your Mac")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:8001")


if __name__ == "__main__":
    asyncio.run(main())
