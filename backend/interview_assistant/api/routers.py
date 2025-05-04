import uuid
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse

from ..core.model import UploadResponse
from ..service.llm_service import LLMService

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_data(
    task: str = Form(...),
    programming_language: str = Form(...),
):
    """
    Обрабатывает запрос на генерацию кода
    
    Args:
        task: Текст задачи
        programming_language: Выбранный язык программирования
    
    Returns:
        UploadResponse: Ответ с уникальным ID сессии и результатом обработки LLM
    """
    try:
        # Генерация уникального ID сессии
        session_id = str(uuid.uuid4())
        
        # Обработка задания с помощью LLM
        message, llm_response = LLMService.process_task(task, programming_language)
        
        # Формирование ответа
        return UploadResponse(
            session_id=session_id,
            message=message,
            llm_response=llm_response,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

@router.get("/")
async def root():
    """Корневой эндпоинт для проверки работоспособности"""
    return {"message": "Interview Assistant Backend is running"}