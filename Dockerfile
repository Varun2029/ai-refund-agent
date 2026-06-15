# ============================================================================
# AI Customer Support Operations Platform
# ============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required by psycopg2 and faiss-cpu
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Create a non-root user (required by Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user . $HOME/app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

# Run seed script and start server
CMD ["sh", "-c", "python -m app.db.seed && uvicorn app.main:app --host 0.0.0.0 --port 7860"]
