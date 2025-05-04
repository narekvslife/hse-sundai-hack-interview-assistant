from langchain_ollama import ChatOllama
from ..core.config import MODEL_NAME, MODEL_TEMPERATURE, PROMPT_TEXT
from typing import Tuple, Optional
from langchain_core.messages import SystemMessage, HumanMessage
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
            llm = ChatOllama(
                model=MODEL_NAME,
                temperature=MODEL_TEMPERATURE,
            )

            prompt_parse = "FROM THIS HTML EXTRACT THE part with the PROGRAMMING PROBLEM FROM CODEFORCES"

            llm_response_parsed = llm.invoke([SystemMessage(content=prompt_parse), HumanMessage(content=task)])

            prompt_solve = f"""SOLVE the following problem USING {programming_language} FAST AND CORRECTLY OTHERWISE YOU WILL BE FIRED:

            {llm_response_parsed.content}

            return only the code in the {programming_language} language
            """

            llm_response = llm.invoke([SystemMessage(content=prompt_solve), HumanMessage(content=llm_response_parsed)])

            if llm_response:
                return "Data uploaded and LLM processed successfully", llm_response.content
            else:
                return "Data uploaded, but no LLM response generated", None
                
        except Exception as e:
            error_message = f"Error running LLM: {str(e)}"
            return "Data uploaded but LLM processing failed", error_message