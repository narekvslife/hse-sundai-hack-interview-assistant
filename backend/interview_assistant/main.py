import os
import uuid
import ollama
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(title="Interview Assistant Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins including chrome extensions
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Directory for storing files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load prompt from file
PROMPT_FILE = "prompt.txt"
if os.path.exists(PROMPT_FILE):
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt = f.read()

model_name = 'qwen2.5-coder:32b'

# Pydantic model for response
class UploadResponse(BaseModel):
    session_id: str
    message: str
    llm_response: str | None

# Endpoint to handle data upload and LLM request
@app.post("/upload", response_model=UploadResponse)
async def upload_data(
    task: str = Form(...),
    programming_language: str = Form(...),
):
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Run inference with local LLM (using ChatOllama)
        llm_response = None
        try:
            # Prepare input for the LLM
            task = task or ""
            llm_input_system = f"""
            Prompt: {prompt}
            Programming Language: {programming_language}
            """
            # Call the local LLM
            llm = ChatOllama(
                model=model_name,
                temperature=0,
            )
            messages = [
                ("system", llm_input_system),
                ("human", task),
            ]
            llm_response = llm.invoke(messages)
        except Exception as e:
            llm_response = f"Error running LLM: {str(e)}"

        return UploadResponse(
            session_id=session_id,
            message="Data uploaded and LLM processed successfully",
            llm_response=llm_response.content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

# Root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Interview Assistant Backend is running"}

def run():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    run()