# ChromaDB Docker Image for FC Knowledge Base
# Uses ChromaDB's official image with persistence support

FROM chromadb/chroma:latest

# Set environment variables for ChromaDB
ENV CHROMA_SERVER_AUTH_PROVIDER="chromadb.auth.token_authn.TokenAuthenticationServerProvider"
ENV CHROMA_SERVER_AUTH_CREDENTIALS="fc-knowledge-base-token"
ENV CHROMA_SERVER_AUTH_TOKEN_TRANSPORT_HEADER="X-Chroma-Token"
ENV IS_PERSISTENT=TRUE
ENV ANONYMIZED_TELEMETRY=FALSE

# Expose the default ChromaDB port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v2/heartbeat || exit 1
