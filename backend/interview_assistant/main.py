import os
import uuid
import ollama
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(title="Interview Assistant Backend")

# Directory for storing files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# SQLite database setup
DATABASE_URL = "sqlite:///interview_data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Load prompt from file
PROMPT_FILE = "prompt.txt"
if os.path.exists(PROMPT_FILE):
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt = f.read()

# Database model
class InterviewData(Base):
    __tablename__ = "interview_data"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    programming_language = Column(String)
    prompt = Column(String)
    html_path = Column(String)
    screenshot_path = Column(String)
    voice_path = Column(String, nullable=True)
    llm_response = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Pydantic model for response
class UploadResponse(BaseModel):
    session_id: str
    message: str
    llm_response: str | None

# Endpoint to handle data upload and LLM request
@app.post("/upload", response_model=UploadResponse)
async def upload_data(
    html_code: str = Form(...),
    screenshot: UploadFile = File(None),
    programming_language: str = Form(...),
    voice_recording: UploadFile = File(None)
):
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(UPLOAD_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)

        # Save HTML code
        html_path = os.path.join(session_dir, "page.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_code)
    
        # Save screenshot (if provided)
        screenshot_path = None
        if screenshot:
            if not screenshot.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Screenshot must be an image")
            screenshot_path = os.path.join(session_dir, screenshot.filename)
            with open(screenshot_path, "wb") as f:
                f.write(await screenshot.read())

        # Save voice recording (if provided)
        voice_path = None
        if voice_recording:
            if not voice_recording.content_type.startswith("audio/"):
                raise HTTPException(status_code=400, detail="Voice recording must be an audio file")
            voice_path = os.path.join(session_dir, voice_recording.filename)
            with open(voice_path, "wb") as f:
                f.write(await voice_recording.read())

        # Run inference with local LLM (using Ollama)
        llm_response = None
        try:
            # Prepare input for the LLM (adjust based on your model's requirements)
            llm_input = f"""
            Prompt: {prompt}
            Programming Language: {programming_language}
            HTML Code: {html_code}
            """
            # Call the local LLM (e.g., gemma2:2b)
            response = ollama.generate(
                model="qwen2.5-coder:32b",
                prompt=llm_input,
            )
            llm_response = response["response"]
        except Exception as e:
            llm_response = f"Error running LLM: {str(e)}"

        # Store metadata in database
        db = SessionLocal()
        try:
            db_data = InterviewData(
                session_id=session_id,
                programming_language=programming_language,
                prompt=prompt,
                html_path=html_path,
                screenshot_path=screenshot_path,
                voice_path=voice_path,
                llm_response=llm_response
            )
            db.add(db_data)
            db.commit()
        finally:
            db.close()

        return UploadResponse(
            session_id=session_id,
            message="Data uploaded and LLM processed successfully",
            llm_response=llm_response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

# Root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Interview Assistant Backend is running"}


def run():
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
if __name__ == "__main__":
    run()