import asyncio
import os
import requests
import zipfile
from tqdm import tqdm

MODELS = {
    "small-ru": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip",
        "dir": "vosk-model-small-ru-0.22"
    },
    "ru": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip",
        "dir": "vosk-model-ru-0.42"
    },
    "small-en": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "dir": "vosk-model-small-en-us-0.15"
    }
}

def download_model(model_name: str = "small-ru", models_dir: str = "models"):
    """
    Автоматически скачивает и распаковывает выбранную модель
    """
    if model_name not in MODELS:
        raise ValueError(f"Доступные модели: {', '.join(MODELS.keys())}")

    model_info = MODELS[model_name]
    model_path = os.path.join(models_dir, model_info['dir'])
    zip_path = os.path.join(models_dir, f"{model_name}.zip")

    # Создаем директорию, если не существует
    os.makedirs(models_dir, exist_ok=True)

    # Проверяем, не скачана ли уже модель
    if os.path.exists(model_path):
        print(f"Модель {model_name} уже установлена")
        return model_path

    print(f"Скачивание модели {model_name}...")
    
    try:
        # Загрузка с прогресс-баром
        response = requests.get(model_info['url'], stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(zip_path, 'wb') as f, tqdm(
            desc=model_name,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)

        # Распаковка
        print("Распаковка...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(models_dir)

        # Удаление ZIP-архива
        os.remove(zip_path)
        
        print(f"Модель {model_name} успешно установлена в {model_path}")
        return model_path

    except Exception as e:
        # Удаляем частично скачанные файлы при ошибке
        if os.path.exists(zip_path):
            os.remove(zip_path)
        raise RuntimeError(f"Ошибка загрузки модели: {str(e)}")


async def main():
    path = download_model("small-ru")

if __name__ == "__main__":
    
    asyncio.run(main())