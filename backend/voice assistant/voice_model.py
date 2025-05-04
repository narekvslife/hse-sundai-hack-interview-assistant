from voice_model_interface import VoiceModelInterface
from vosk import Model, KaldiRecognizer
import wave
import json
import os
from typing import Optional

class VoiceModel(VoiceModelInterface):
    def __init__(self):
        super().__init__()
        self.model: Optional[Model] = None
        self.is_active: bool = False
        
    async def init_model(self, model_path: str) -> None:
        """Инициализация модели с проверкой пути"""
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model path {model_path} not found")
                
            self.model = Model(model_path)
            self.is_active = True
            print(f"Model {model_path} loaded successfully")
        except Exception as e:
            self.is_active = False
            raise RuntimeError(f"Model initialization failed: {str(e)}") from e
        
    async def get_text(self, audio_path: str) -> str:
        """Распознавание текста с обработкой ошибок"""
        if not self.is_active or self.model is None:
            raise RuntimeError("Model not initialized. Call init_model() first")
            
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file {audio_path} not found")

        try:
            with wave.open(audio_path, "rb") as wf:
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                    raise ValueError("Audio must be WAV format mono PCM")
                    
                recognizer = KaldiRecognizer(self.model, wf.getframerate())
                results = []
                
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if recognizer.AcceptWaveform(data):
                        res = json.loads(recognizer.Result())
                        results.append(res.get("text", ""))
                
                final_res = json.loads(recognizer.FinalResult())
                results.append(final_res.get("text", ""))
                
                return " ".join(filter(None, results)).strip()
                
        except wave.Error as e:
            raise ValueError(f"Invalid audio file: {str(e)}") from e
            
    async def get_status(self) -> bool:
        """Статус модели"""
        return self.is_active and self.model is not None