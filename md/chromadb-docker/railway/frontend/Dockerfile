# Product Owner RAG - Frontend Service for Railway
# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY product-owner-rag/requirements.txt .

# Install dependencies with BuildKit cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy shared modules
COPY config.py /app/
COPY titan_v1_embeddings.py /app/

# Copy application
COPY product-owner-rag/app.py .

# Railway uses PORT environment variable
ENV PORT=8501

# Expose port (Railway will map this)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/_stcore/health || exit 1

# Run Streamlit - Railway sets PORT automatically
CMD streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true
