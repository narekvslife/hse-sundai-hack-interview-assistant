import uuid
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import StreamingResponse

from ..service.llm_service import LLMService

router = APIRouter()

@router.post("/upload")
async def upload_data(
    task: str = Form(...),
    programming_language: str = Form(...),
):
    """
    Обрабатывает запрос на генерацию кода в потоковом режиме
    
    Args:
        task: Текст задачи
        programming_language: Выбранный язык программирования
    
    Returns:
        StreamingResponse: Поток с частями генерируемого кода
    """
    try:
        # Получение асинхронного генератора из сервиса LLM
        llm_stream = LLMService.stream_task(task, programming_language)

        # Возврат потокового ответа
        return StreamingResponse(llm_stream, media_type="text/plain")

    except Exception as e:
        # Логирование ошибки может быть добавлено здесь
        print(f"Error initiating stream: {str(e)}") # Added print for debugging
        raise HTTPException(status_code=500, detail=f"Error initiating stream: {str(e)}")

@router.get("/")
async def root():
    """Корневой эндпоинт для проверки работоспособности"""
    return {"message": "Interview Assistant Backend is running"}