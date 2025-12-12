# Product Owner RAG - Streamlit Application
# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Install dependencies with BuildKit cache mount for faster rebuilds
# The cache mount persists pip's download cache across builds
COPY product-owner-rag/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy shared modules from chromadb-docker directory (build context is md/)
COPY chromadb-docker/config.py /app/
COPY chromadb-docker/titan_v1_embeddings.py /app/

# Copy application from product-owner-rag subdirectory
COPY product-owner-rag/app.py .

# Copy concept map component (bidirectional Streamlit component)
COPY product-owner-rag/concept_map_component /app/concept_map_component

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
