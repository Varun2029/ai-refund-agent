"""
Voice processing API for STT using Groq Whisper.
"""

import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe uploaded audio file using Groq's Whisper model."""
    if not settings.GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured")
        
    try:
        from groq import AsyncGroq
    except ImportError:
        raise HTTPException(status_code=500, detail="groq package not installed")

    # Create temp file
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, audio.filename or "audio.webm")
    
    try:
        # Save upload to temp file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
            
        client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        
        with open(temp_file_path, "rb") as file:
            transcription = await client.audio.transcriptions.create(
              file=(os.path.basename(temp_file_path), file.read()),
              model="whisper-large-v3-turbo",
            )
            
        return {"text": transcription.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        shutil.rmtree(temp_dir, ignore_errors=True)
