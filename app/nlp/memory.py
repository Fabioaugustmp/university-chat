from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConversationTurn:
    role: str
    text: str


@dataclass
class ConversationState:
    session_id: str
    current_topic: str | None = None
    last_intent: str | None = None
    last_discipline: str | None = None
    last_service: str | None = None
    history: list[ConversationTurn] = field(default_factory=list)


class ConversationMemory:
    """Armazena contexto em memoria para cada sessao."""

    def __init__(self) -> None:
        self._sessions: dict[str, ConversationState] = {}

    def get_or_create(self, session_id: str) -> ConversationState:
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationState(session_id=session_id)
        return self._sessions[session_id]

    def add_turn(self, session_id: str, role: str, text: str) -> ConversationState:
        state = self.get_or_create(session_id)
        state.history.append(ConversationTurn(role=role, text=text))
        state.history = state.history[-10:]
        return state
