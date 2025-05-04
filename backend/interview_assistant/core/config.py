import os
from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PROMPT_FILE = os.path.join(BASE_DIR, "prompt.txt")

# Создаем папку для загрузок, если не существует
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Загружаем текст промпта из файла
PROMPT_TEXT = ""
if os.path.exists(PROMPT_FILE):
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        PROMPT_TEXT = f.read()

# Настройки LLM
MODEL_NAME = 'qwen2.5-coder:32b'
MODEL_TEMPERATURE = 0

# Настройки CORS
CORS_ORIGINS = ["*"]  # В продакшене лучше указать конкретные домены
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# Настройки приложения
APP_TITLE = "Interview Assistant Backend"