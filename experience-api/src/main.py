from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class URLItem(BaseModel):
    url: str

@app.post("/process-url")
async def process_url(item: URLItem):
    """
    Accepts a URL string, downloads and transcribes the content.
    For now, this is a placeholder.
    """
    url = item.url
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")

    print(f"Received URL for processing: {url}")

    # Simulate processing
    processed_content = f"Content from {url} processed and transcribed (placeholder)."

    return {"message": "URL received and processing initiated", "url": url, "processed_content": processed_content}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Experience API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)