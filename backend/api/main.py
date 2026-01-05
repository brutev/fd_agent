from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
import time
import logging
from contextlib import asynccontextmanager

from config import settings
from api.routes import auth, accounts, transactions, kyc, loans
from api.middleware.rate_limit import RateLimitMiddleware
from api.middleware.auth import AuthMiddleware
from memory.vector_store import VectorStore
from memory.structured_store import StructuredStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize stores
vector_store = None
structured_store = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global vector_store, structured_store
    vector_store = VectorStore()
    structured_store = StructuredStore()
    await structured_store.init_db()
    logger.info("Application started")
    yield
    # Shutdown
    logger.info("Application shutdown")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI-powered Financial Domain Agent System",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure for production
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# Routes - note: routers already have their own prefix (e.g., /auth, /accounts)
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(accounts.router, prefix=settings.API_V1_STR, tags=["accounts"])
app.include_router(transactions.router, prefix=settings.API_V1_STR, tags=["transactions"])
app.include_router(kyc.router, prefix=settings.API_V1_STR, tags=["kyc"])
app.include_router(loans.router, prefix=settings.API_V1_STR, tags=["loans"])

@app.get("/")
async def root():
    return {"message": "FD Agent System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)