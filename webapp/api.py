from quart import Blueprint, request, jsonify
from .schemas import ChatRequest, ChatResponse, ChatMessage
import uuid

bp = Blueprint("api", __name__)


@bp.route("/chat", methods=["POST"])
async def chat():
    """Simple demo chat endpoint that returns a structured Pydantic response.

    This echoes the user message and wraps it in a ChatResponse to demonstrate
    structured output and validation.
    """
    payload = await request.get_json(force=True)
    req = ChatRequest(**payload)

    # Simple echo logic for demo; replace with real model integration later.
    assistant_text = f"Echo: {req.message}"

    response = ChatResponse(
        id=str(uuid.uuid4()),
        model="demo-echo-1",
        choices=[ChatMessage(role="assistant", content=assistant_text)],
    )

    return jsonify(response.model_dump())
