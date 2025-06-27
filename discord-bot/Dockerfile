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

# Copy dependency files (only pyproject.toml is needed now)
COPY pyproject.toml ./
# If you have a uv.lock file and want to ensure reproducible installs, copy that too:
# COPY uv.lock ./

RUN uv venv && uv pip install --system -e .

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --shell /bin/bash botuser \
    && chown -R botuser:botuser /app
USER botuser

# Health check script
COPY --chown=botuser:botuser <<EOF /app/health_check.py
import sys
import logging
from config import Config

def health_check():
    try:
        # Basic configuration validation
        # Ensure your Config.validate() does not rely on specific files not copied yet
        # or that it can function within the Docker build context.
        # It's generally better to validate only essential environment variables
        # for a health check at this stage.
        Config.validate()
        print("Health check passed")
        return 0
    except Exception as e:
        print(f"Health check failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(health_check())
EOF

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python health_check.py || exit 1

# Run the bot
CMD ["python", "src/bot.py"]
