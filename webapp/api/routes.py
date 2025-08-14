"""API blueprint routes."""
from quart import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from typing import Optional
import logging

from ..llm import LLMService, ChatRequest, create_error_response
from ..schemas import ChatRequest as LegacyChatRequest, ChatResponse as LegacyChatResponse, ChatMessage

bp = Blueprint("api", __name__)
logger = logging.getLogger(__name__)

# Global LLM service instance
llm_service: Optional[LLMService] = None


async def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service


@bp.route("/health", methods=["GET"])
async def health_check():
    """Health check endpoint that also checks LLM service."""
    try:
        service = await get_llm_service()
        llm_healthy = await service.health_check()
        
        return jsonify({
            "status": "healthy" if llm_healthy else "degraded",
            "llm_service": "connected" if llm_healthy else "disconnected",
            "timestamp": "2025-01-14T00:00:00Z"  # You'd use datetime.utcnow() in practice
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-01-14T00:00:00Z"
        }), 500


@bp.route("/chat", methods=["POST"])
async def chat():
    """Enhanced chat endpoint with LLM integration and structured output.
    
    Accepts ChatRequest and returns structured ChatResponse using Pydantic validation.
    Supports conversation context and various LLM parameters.
    """
    try:
        # Get and validate request
        payload = await request.get_json(force=True)
        if not payload:
            return jsonify(create_error_response(
                "validation_error", 
                "Request body is required"
            )), 400
        
        # Validate request with new Pydantic schema
        try:
            chat_request = ChatRequest(**payload)
        except ValidationError as e:
            return jsonify(create_error_response(
                "validation_error",
                "Invalid request format",
                {"validation_errors": e.errors()}
            )), 400
        
        # Get LLM service and process request
        service = await get_llm_service()
        
        # Check if service is healthy
        if not await service.health_check():
            return jsonify(create_error_response(
                "service_unavailable",
                "LLM service is not available"
            )), 503
        
        # Process the chat request
        response = await service.process_chat_request(chat_request)
        
        # Return structured response
        return jsonify(response.model_dump())
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return jsonify(create_error_response(
            "validation_error",
            "Invalid data format",
            {"errors": e.errors()}
        )), 400
    
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify(create_error_response(
            "internal_error",
            "An internal error occurred"
        )), 500


@bp.route("/chat/legacy", methods=["POST"])
async def chat_legacy():
    """Legacy chat endpoint for backward compatibility.
    
    This maintains the original simple echo functionality for testing.
    """
    try:
        payload = await request.get_json(force=True)
        req = LegacyChatRequest(**payload)

        # Simple echo logic for demo; replace with real model integration later.
        assistant_text = f"Echo: {req.message}"

        response = LegacyChatResponse(
            id="legacy-" + str(hash(req.message) % 100000),
            model="demo-echo-1",
            choices=[ChatMessage(role="assistant", content=assistant_text)],
        )

        return jsonify(response.model_dump())
    
    except Exception as e:
        logger.error(f"Legacy chat error: {e}")
        return jsonify({"error": "Invalid request format"}), 400


@bp.route("/analyze", methods=["POST"])
async def analyze_input():
    """Analyze user input to understand intent and provide structured analysis."""
    try:
        payload = await request.get_json(force=True)
        user_input = payload.get("input", "").strip()
        
        if not user_input:
            return jsonify(create_error_response(
                "validation_error",
                "Input text is required"
            )), 400
        
        service = await get_llm_service()
        analysis = await service.analyze_user_input(user_input)
        
        return jsonify({
            "input": user_input,
            "analysis": analysis
        })
        
    except Exception as e:
        logger.error(f"Analysis endpoint error: {e}")
        return jsonify(create_error_response(
            "internal_error",
            "Analysis failed"
        )), 500


@bp.route("/structured-output", methods=["POST"])
async def structured_output():
    """Generate structured output based on a schema."""
    try:
        payload = await request.get_json(force=True)
        prompt = payload.get("prompt", "").strip()
        schema = payload.get("schema", {})
        system_prompt = payload.get("system_prompt")
        
        if not prompt:
            return jsonify(create_error_response(
                "validation_error",
                "Prompt is required"
            )), 400
        
        service = await get_llm_service()
        result = await service.generate_with_structured_output(
            prompt=prompt,
            output_schema=str(schema),
            system_prompt=system_prompt
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Structured output endpoint error: {e}")
        return jsonify(create_error_response(
            "internal_error",
            "Structured output generation failed"
        )), 500


# Cleanup function for app teardown
async def cleanup_llm_service():
    """Cleanup LLM service resources."""
    global llm_service
    if llm_service:
        await llm_service.cleanup()
        llm_service = None
