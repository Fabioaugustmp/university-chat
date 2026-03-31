import re
import unicodedata


class TextPreprocessor:
    """Realiza uma limpeza simples e didatica para o texto do usuario."""

    _url_pattern = re.compile(r"https?://\S+|www\.\S+")
    _space_pattern = re.compile(r"\s+")
    _punctuation_pattern = re.compile(r"[^\w\s]")

    def __init__(self, remove_accents: bool = True) -> None:
        self.remove_accents = remove_accents

    def normalize(self, text: str) -> str:
        cleaned = text.strip().lower()
        cleaned = self._url_pattern.sub(" ", cleaned)
        cleaned = self._punctuation_pattern.sub(" ", cleaned)
        if self.remove_accents:
            cleaned = self._strip_accents(cleaned)
        cleaned = self._space_pattern.sub(" ", cleaned)
        return cleaned.strip()

    @staticmethod
    def _strip_accents(text: str) -> str:
        normalized = unicodedata.normalize("NFD", text)
        return "".join(char for char in normalized if unicodedata.category(char) != "Mn")
