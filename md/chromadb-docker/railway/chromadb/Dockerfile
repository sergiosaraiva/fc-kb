# ChromaDB Service for Railway
# Based on official ChromaDB image with Railway-specific configuration
FROM chromadb/chroma:0.5.23

# Railway configuration
ENV PORT=8000
ENV IS_PERSISTENT=TRUE
ENV ANONYMIZED_TELEMETRY=FALSE
ENV CHROMA_HOST_ADDR=::
ENV CHROMA_HOST_PORT=8000

# Persistence directory (Railway volume should mount here)
ENV PERSIST_DIRECTORY=/chroma/chroma

# Auth configuration (set these in Railway dashboard)
# ENV CHROMA_SERVER_AUTH_PROVIDER=chromadb.auth.token_authn.TokenAuthenticationServerProvider
# ENV CHROMA_SERVER_AUTH_CREDENTIALS=your-token
# ENV CHROMA_SERVER_AUTH_TOKEN_TRANSPORT_HEADER=X-Chroma-Token

EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/heartbeat || exit 1
