from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Mensagem enviada pelo usuario.")
    session_id: str | None = Field(default=None, description="Identificador da conversa.")


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    intent: str
    confidence: float
    current_topic: str | None
    used_bert: bool
    ranking: list[tuple[str, float]]
    extracted: dict[str, str]
