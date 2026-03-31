from fastapi import APIRouter, Request

from app.api.schemas import ChatRequest, ChatResponse


router = APIRouter(prefix="/api", tags=["chat"])


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    engine = request.app.state.chat_engine
    response = engine.respond(message=payload.message, session_id=payload.session_id)
    return ChatResponse(**response.to_dict())
