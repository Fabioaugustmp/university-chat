from __future__ import annotations

from dataclasses import asdict, dataclass
from uuid import uuid4

from app.core.config import ALLOW_BERT_DOWNLOAD, DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_MODEL_NAME
from app.data.knowledge_base import AcademicKnowledgeBase, Discipline, ServiceInfo
from app.nlp.bert_encoder import BertEmbeddingService
from app.nlp.intent_classifier import IntentClassifier, IntentPrediction
from app.nlp.memory import ConversationMemory, ConversationState
from app.nlp.preprocessing import TextPreprocessor


@dataclass
class ChatEngineResponse:
    session_id: str
    reply: str
    intent: str
    confidence: float
    current_topic: str | None
    used_bert: bool
    ranking: list[tuple[str, float]]
    extracted: dict[str, str]

    def to_dict(self) -> dict:
        return asdict(self)


class AcademicChatEngine:
    """Coordena limpeza, classificacao, memoria e resposta final."""

    def __init__(self) -> None:
        self.preprocessor = TextPreprocessor()
        self.knowledge_base = AcademicKnowledgeBase()
        self.embedding_service = BertEmbeddingService(
            DEFAULT_MODEL_NAME,
            allow_download=ALLOW_BERT_DOWNLOAD,
        )
        self.intent_classifier = IntentClassifier(self.knowledge_base, self.embedding_service)
        self.memory = ConversationMemory()

    def respond(self, message: str, session_id: str | None = None) -> ChatEngineResponse:
        session_id = session_id or str(uuid4())
        state = self.memory.add_turn(session_id, role="user", text=message)

        clean_text = self.preprocessor.normalize(message)
        prediction = self.intent_classifier.predict(clean_text)

        discipline = self.knowledge_base.detect_discipline(clean_text)
        service = self.knowledge_base.detect_service(clean_text)

        intent = self._resolve_intent(clean_text, prediction, state, discipline, service)
        reply, extracted = self._build_reply(intent, clean_text, state, discipline, service)

        state.last_intent = intent
        state.current_topic = extracted.get("topic", state.current_topic)
        state.last_discipline = extracted.get("discipline", state.last_discipline)
        state.last_service = extracted.get("service", state.last_service)
        self.memory.add_turn(session_id, role="assistant", text=reply)

        return ChatEngineResponse(
            session_id=session_id,
            reply=reply,
            intent=intent,
            confidence=prediction.confidence,
            current_topic=state.current_topic,
            used_bert=prediction.used_bert,
            ranking=prediction.ranking,
            extracted=extracted,
        )

    def _resolve_intent(
        self,
        clean_text: str,
        prediction: IntentPrediction,
        state: ConversationState,
        discipline: Discipline | None,
        service: ServiceInfo | None,
    ) -> str:
        if discipline and "professor" in clean_text:
            return "professor_info"
        if discipline:
            return prediction.name if prediction.name in {"disciplina_info", "professor_info"} else "disciplina_info"
        if service and "valor" in clean_text:
            return "financeiro"
        if service:
            return prediction.name if prediction.name in {"secretaria", "financeiro"} else "secretaria"

        if prediction.name == "follow_up" or prediction.confidence < DEFAULT_CONFIDENCE_THRESHOLD:
            contextual_intent = self._infer_follow_up(clean_text, state)
            if contextual_intent:
                return contextual_intent

        return prediction.name

    def _infer_follow_up(self, clean_text: str, state: ConversationState) -> str | None:
        if not state.last_intent:
            return None
        if any(term in clean_text for term in ["valor", "prazo", "como", "isso", "depois", "professor"]):
            return state.last_intent
        return None

    def _build_reply(
        self,
        intent: str,
        clean_text: str,
        state: ConversationState,
        discipline: Discipline | None,
        service: ServiceInfo | None,
    ) -> tuple[str, dict[str, str]]:
        extracted: dict[str, str] = {}

        if intent == "saudacao":
            extracted["topic"] = "abertura"
            return (
                "Ola! Eu sou o Assistente Academico Inteligente. Posso ajudar com secretaria, "
                "financeiro, disciplinas, professores e perguntas de continuidade.",
                extracted,
            )

        if intent == "agradecimento":
            extracted["topic"] = state.current_topic or "encerramento"
            return "Por nada! Se quiser, posso continuar a conversa a partir do assunto atual.", extracted

        if intent == "despedida":
            extracted["topic"] = "encerramento"
            return "Ate mais! Quando quiser, podemos continuar do ponto em que paramos.", extracted

        if intent == "professor_info":
            chosen = discipline or self._discipline_from_context(state)
            if chosen:
                extracted["topic"] = "professores"
                extracted["discipline"] = chosen.name
                return f"O professor responsavel por {chosen.name} e {chosen.professor}.", extracted
            return "Posso informar o professor se voce me disser o nome da disciplina.", extracted

        if intent == "disciplina_info":
            chosen = discipline or self._discipline_from_context(state)
            if chosen:
                extracted["topic"] = "disciplinas"
                extracted["discipline"] = chosen.name
                topics = ", ".join(chosen.topics)
                return (
                    f"Na disciplina {chosen.name}, voce vai estudar {chosen.summary} "
                    f"Alguns topicos centrais sao: {topics}.",
                    extracted,
                )
            return "Consigo explicar a disciplina se voce citar, por exemplo, IA Aplicada, Redes ou PLN.", extracted

        if intent == "financeiro":
            chosen = service or self._service_from_context(state)
            if chosen:
                extracted["topic"] = "financeiro"
                extracted["service"] = chosen.topic
                if "valor" in clean_text and chosen.amount:
                    return f"Sobre {chosen.topic}, {chosen.amount}", extracted
                if "prazo" in clean_text or "venc" in clean_text:
                    return f"Sobre {chosen.topic}, {chosen.deadline}", extracted
                return f"{chosen.guidance} {chosen.deadline}", extracted
            return "Posso ajudar com boleto, mensalidade ou valor de matricula se voce disser o servico.", extracted

        if intent == "secretaria":
            chosen = service or self._service_from_context(state)
            if chosen:
                extracted["topic"] = "secretaria"
                extracted["service"] = chosen.topic
                if "valor" in clean_text and chosen.amount:
                    return f"Sobre {chosen.topic}, {chosen.amount}", extracted
                return f"{chosen.guidance} {chosen.deadline}", extracted
            return "Posso orientar sobre historico, matricula e outros servicos da secretaria.", extracted

        extracted["topic"] = state.current_topic or "geral"
        return (
            "Ainda nao entendi totalmente sua pergunta. Tente reformular mencionando o assunto, "
            "como historico, boleto, IA Aplicada ou professor de uma disciplina.",
            extracted,
        )

    def _discipline_from_context(self, state: ConversationState) -> Discipline | None:
        if not state.last_discipline:
            return None
        normalized = self.preprocessor.normalize(state.last_discipline)
        return self.knowledge_base.detect_discipline(normalized)

    def _service_from_context(self, state: ConversationState) -> ServiceInfo | None:
        if not state.last_service:
            return None
        normalized = self.preprocessor.normalize(state.last_service)
        return self.knowledge_base.detect_service(normalized)
