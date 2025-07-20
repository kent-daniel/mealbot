from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import AsyncIterator
from faster_whisper import WhisperModel # Import WhisperModel from faster_whisper

from .video_pipeline import process_video_url, download_audio, transcribe_audio, save_transcript_to_json # Import individual functions

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Load the Whisper model on startup
    print("Loading Faster Whisper model...")
    # Use "tiny" model, device "cpu", and compute_type "int8" for efficiency
    app.state.whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
    print("Faster Whisper model loaded.")
    yield
    # Clean up on shutdown (if any)
    print("Application shutdown.")

app = FastAPI(lifespan=lifespan)

class URLItem(BaseModel):
    video_url: str
    source: str

@app.post("/process-url")
async def process_url_endpoint(item: URLItem):
    """
    Accepts a URL string, downloads and transcribes the content.
    """
    url = item.url
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")

    try:
        # Pass the pre-loaded model to the video pipeline
        transcript = process_video_url(url, app.state.whisper_model)
        return {"url": url, "transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {e}")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Experience API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import os
    import uvicorn # Import uvicorn here
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
