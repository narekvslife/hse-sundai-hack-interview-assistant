from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    """Модель ответа для эндпоинта загрузки"""
    session_id: str
    message: str
    llm_response: Optional[str] = None