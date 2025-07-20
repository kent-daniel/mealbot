# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_CACHE_DIR=/tmp/uv-cache

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install ffmpeg for audio processing
RUN apt-get update && apt-get install -y ffmpeg

COPY pyproject.toml ./

RUN uv venv && uv pip install --system -e .

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
