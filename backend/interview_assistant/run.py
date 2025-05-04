import uvicorn
from app.main import app

def run():
    """Запускает сервер FastAPI"""
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    run()