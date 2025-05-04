from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from interview_assistant.core.config import (
    APP_TITLE,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS
)
from interview_assistant.api.routers import router

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

def run():
     import uvicorn
     uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
     
if __name__ == "__main__":
    run()