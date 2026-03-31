from __future__ import annotations

from dataclasses import dataclass

from app.data.knowledge_base import AcademicKnowledgeBase, IntentDefinition
from app.nlp.bert_encoder import BertEmbeddingService


@dataclass
class IntentPrediction:
    name: str
    confidence: float
    ranking: list[tuple[str, float]]
    used_bert: bool


class IntentClassifier:
    """Classifica intencoes com BERT e faz fallback para regras simples."""

    def __init__(self, knowledge_base: AcademicKnowledgeBase, embedding_service: BertEmbeddingService) -> None:
        self.knowledge_base = knowledge_base
        self.embedding_service = embedding_service
        self._example_index: list[tuple[IntentDefinition, str]] = []
        self._example_vectors: list[list[float]] = []
        self._vectors_ready = False

        for intent in self.knowledge_base.iter_intents():
            for example in intent.examples:
                self._example_index.append((intent, example))

    def predict(self, message: str) -> IntentPrediction:
        if self._prepare_vectors():
            return self._predict_with_bert(message)
        return self._predict_with_keywords(message)

    def _prepare_vectors(self) -> bool:
        if self._vectors_ready:
            return True

        texts = [example for _, example in self._example_index]
        result = self.embedding_service.encode(texts)
        if not result.available:
            return False

        self._example_vectors = result.vectors
        self._vectors_ready = True
        return True

    def _predict_with_bert(self, message: str) -> IntentPrediction:
        result = self.embedding_service.encode([message])
        if not result.available or not result.vectors:
            return self._predict_with_keywords(message)

        message_vector = result.vectors[0]
        scores: dict[str, float] = {}
        for (intent, _example), vector in zip(self._example_index, self._example_vectors):
            similarity = self.embedding_service.cosine_similarity(message_vector, vector)
            current = scores.get(intent.name, 0.0)
            scores[intent.name] = max(current, similarity)

        ranking = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        best_name, best_score = ranking[0]
        return IntentPrediction(
            name=best_name,
            confidence=round(float(best_score), 4),
            ranking=[(name, round(score, 4)) for name, score in ranking[:5]],
            used_bert=True,
        )

    def _predict_with_keywords(self, message: str) -> IntentPrediction:
        tokens = set(message.split())
        scores: dict[str, float] = {}

        for intent in self.knowledge_base.iter_intents():
            matches = sum(1 for keyword in intent.keywords if keyword in message or keyword in tokens)
            if matches:
                scores[intent.name] = matches / max(len(intent.keywords), 1)

        if not scores:
            return IntentPrediction(
                name="fallback",
                confidence=0.0,
                ranking=[("fallback", 0.0)],
                used_bert=False,
            )

        ranking = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        best_name, best_score = ranking[0]
        return IntentPrediction(
            name=best_name,
            confidence=round(float(best_score), 4),
            ranking=[(name, round(score, 4)) for name, score in ranking[:5]],
            used_bert=False,
        )
