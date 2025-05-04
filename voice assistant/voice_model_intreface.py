from abc import ABC, abstractmethod

class VoiceModelInterface(ABC):
    
    @abstractmethod
    async def init_model(self, name : str = "") -> None:
        pass
        
    @abstractmethod
    async def get_text(self, path : str = "") -> str:
        pass
        
    @abstractmethod
    async def get_status(self) -> bool:
        pass
    