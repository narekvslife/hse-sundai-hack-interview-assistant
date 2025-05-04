from langchain_ollama import ChatOllama
from ..core.config import MODEL_NAME, MODEL_TEMPERATURE, PROMPT_TEXT
from typing import Tuple, Optional, AsyncGenerator
from langchain_core.messages import BaseMessageChunk

class LLMService:
    """Сервис для работы с языковой моделью"""
    
    @staticmethod
    def process_task(task: str, programming_language: str) -> Tuple[str, Optional[str]]:
        """
        Обрабатывает задачу с помощью LLM
        
        Args:
            task: Текст задачи
            programming_language: Язык программирования для решения
            
        Returns:
            Tuple[str, Optional[str]]: Сообщение о статусе и ответ от LLM
        """
        try:
            # Подготовка входных данных для LLM
            llm_input_system = f"""
            Prompt: {PROMPT_TEXT}
            Programming Language: {programming_language}
            """
            
            # Вызов локальной LLM
            llm = ChatOllama(
                model=MODEL_NAME,
                temperature=MODEL_TEMPERATURE,
            )
            
            messages = [
                ("system", llm_input_system),
                ("human", task or ""),
            ]
            
            # Получение ответа от LLM
            llm_response = llm.invoke(messages)
            
            if llm_response:
                return "Data uploaded and LLM processed successfully", llm_response.content
            else:
                return "Data uploaded, but no LLM response generated", None
                
        except Exception as e:
            error_message = f"Error running LLM: {str(e)}"
            return "Data uploaded but LLM processing failed", error_message

    @staticmethod
    async def stream_task(task: str, programming_language: str) -> AsyncGenerator[str, None]:
        """
        Обрабатывает задачу с помощью LLM в потоковом режиме.
        
        Args:
            task: Текст задачи
            programming_language: Язык программирования для решения
            
        Yields:
            str: Части ответа от LLM
        """
        try:
            llm_input_system = f"""
            Prompt: {PROMPT_TEXT}
            Programming Language: {programming_language}
            """
            
            llm = ChatOllama(
                model=MODEL_NAME,
                temperature=MODEL_TEMPERATURE,
            )
            
            messages = [
                ("system", llm_input_system),
                ("human", task or ""),
            ]

            async for chunk in llm.astream(messages):
                if isinstance(chunk, BaseMessageChunk) and chunk.content:
                    yield chunk.content
        except Exception as e:
            # Log the error for debugging
            print(f"Error during LLM stream: {str(e)}") 
            # Yield an error message to the client if possible
            yield f"Error during generation: {str(e)}"