from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import (
    APP_TITLE,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS
)
from app.api.routes import router

def create_application() -> FastAPI:
    """
    Создает и настраивает экземпляр FastAPI приложения
    
    Returns:
        FastAPI: Настроенное приложение
    """
    # Инициализация FastAPI
    app = FastAPI(title=APP_TITLE)
    
    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_ALLOW_CREDENTIALS,
        allow_methods=CORS_ALLOW_METHODS,
        allow_headers=CORS_ALLOW_HEADERS,
    )
    
    # Подключение маршрутов
    app.include_router(router)
    
    return app

# Создание приложения
app = create_application()