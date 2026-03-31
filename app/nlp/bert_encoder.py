from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass
class EncodingResult:
    vectors: list[list[float]]
    model_name: str
    available: bool


class BertEmbeddingService:
    """
    Gera embeddings com BERT usando mean pooling.

    O carregamento e feito de forma tardia para que a aplicacao continue
    funcional mesmo quando o modelo nao estiver disponivel localmente.
    """

    def __init__(self, model_name: str, allow_download: bool = False) -> None:
        self.model_name = model_name
        self.allow_download = allow_download
        self._tokenizer = None
        self._model = None
        self._torch = None
        self.available = False
        self.error_message: str | None = None

    def encode(self, texts: Sequence[str]) -> EncodingResult:
        self._ensure_loaded()
        if not self.available:
            return EncodingResult(vectors=[], model_name=self.model_name, available=False)

        tokenizer = self._tokenizer
        model = self._model
        torch = self._torch

        encoded_input = tokenizer(
            list(texts),
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="pt",
        )

        with torch.no_grad():
            model_output = model(**encoded_input)

        token_embeddings = model_output.last_hidden_state
        attention_mask = encoded_input["attention_mask"].unsqueeze(-1).expand(token_embeddings.size()).float()
        pooled = (token_embeddings * attention_mask).sum(1) / attention_mask.sum(1).clamp(min=1e-9)
        normalized = torch.nn.functional.normalize(pooled, p=2, dim=1)
        return EncodingResult(
            vectors=normalized.cpu().tolist(),
            model_name=self.model_name,
            available=True,
        )

    def cosine_similarity(self, left: list[float], right: list[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right))
        left_norm = sum(a * a for a in left) ** 0.5
        right_norm = sum(b * b for b in right) ** 0.5
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    def _ensure_loaded(self) -> None:
        if self.available or self.error_message is not None:
            return

        try:
            import torch
            from transformers import AutoModel, AutoTokenizer

            self._torch = torch
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                local_files_only=not self.allow_download,
            )
            self._model = AutoModel.from_pretrained(
                self.model_name,
                local_files_only=not self.allow_download,
            )
            self._model.eval()
            self.available = True
        except Exception as exc:  # pragma: no cover - depende do ambiente
            self.error_message = str(exc)
            self.available = False
