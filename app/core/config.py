import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
APP_DIR = BASE_DIR / "app"
WEB_DIR = APP_DIR / "web"
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"

APP_TITLE = "Assistente Academico Inteligente"
APP_DESCRIPTION = "Exemplo didatico de chatbot academico com FastAPI e PLN."
DEFAULT_MODEL_NAME = "neuralmind/bert-base-portuguese-cased"
DEFAULT_CONFIDENCE_THRESHOLD = 0.35
ALLOW_BERT_DOWNLOAD = os.getenv("ALLOW_BERT_DOWNLOAD", "0") == "1"
